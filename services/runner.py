import asyncio
import traceback
from typing import List
from bots.device_actions import change_device_credentials
from services.json_logger import JsonLogger, make_log_path
from services.state import load_completed, mark_completed


def run_change_passwords(
    ips: List[str],
    current_username: str,
    current_password: str,
    new_username: str,
    new_password: str,
    change_id: str,
    ui_queue,
    stop_flag,
):
    """
    Sync entrypoint launched in a background thread.
    Spawns an asyncio loop and runs the Playwright flow.
    """
    log_path = make_log_path(change_id)
    logger = JsonLogger(log_path)
    ui_queue.put((f"Log file: {log_path}", "INFO"))

    already_done = load_completed(change_id)
    if already_done:
        ui_queue.put(
            (
                f"Resuming: {len(already_done)} device(s) already completed for this credential change.",
                "INFO",
            )
        )

    async def _run():
        for idx, ip in enumerate(ips, start=1):
            if stop_flag.is_set():
                ui_queue.put(("Run aborted.", "ABORT"))
                break

            if ip in already_done:
                ui_queue.put(
                    (f"[{idx}/{len(ips)}] {ip} — skipped (already completed).", "INFO")
                )
                continue

            ui_queue.put((f"[{idx}/{len(ips)}] {ip} — processing…", "INFO"))
            try:
                result = await change_device_credentials(
                    ip=ip,
                    current_username=current_username,
                    current_password=current_password,
                    new_username=new_username,
                    new_password=new_password,
                )
                logger.write({"ip": ip, "status": "ok", "details": result})
                mark_completed(change_id, ip)
                ui_queue.put((f"[{idx}/{len(ips)}] {ip} — success.", "INFO"))
            except Exception as e:
                logger.write(
                    {
                        "ip": ip,
                        "status": "error",
                        "error": str(e),
                        "trace": traceback.format_exc(),
                    }
                )
                ui_queue.put((f"[{idx}/{len(ips)}] {ip} — ERROR: {e}", "INFO"))
        else:
            ui_queue.put(("All devices processed.", "DONE"))

    # Run asyncio loop in this thread
    try:
        asyncio.run(_run())
    except RuntimeError:
        # If there's already a loop (rare in Windows threads), make a new one explicitly
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_run())
        loop.close()
