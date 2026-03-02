# Setting up AVM Scraper on cPanel

This guide explains how to set up the raw market listings scraper as a daily cron job on cPanel.

## Prerequisites

1. **Terminal Access**: You need SSH/Terminal access enabled on your cPanel account.
2. **Python Environment**: You need Python installed (ideally 3.9+) and a virtual environment created in `backend/venv`.
3. **Playwright Dependencies**: Playwright requires browser binaries to run. On shared cPanel hosting, this is often the biggest hurdle.
   - You need to run `playwright install chromium` from within your virtual environment.
   - *Note*: If your cPanel host strict limits memory/CPU or blocks browser OS dependencies, you might need a VPS.

## 1. Configure the Wrapper Script

Open `backend/scraper/cron_scraper.sh` and edit the configuration paths to match your actual cPanel structure:

```bash
# Example paths for cPanel:
APP_DIR="/home/YOUR_CPANEL_USERNAME/public_html/backend"
```

Then make it executable:
```bash
chmod +x /home/YOUR_CPANEL_USERNAME/public_html/backend/scraper/cron_scraper.sh
```

## 2. Set up the Cron Job in cPanel

1. Log into your **cPanel**.
2. Scroll to the **Advanced** section and click on **Cron Jobs**.
3. Under **Add New Cron Job**:
   - **Common Settings**: Choose `Once Per Day (0 0 * * *)` or manually specify a time (e.g. 2 AM `0 2 * * *`).
   - **Command**: Enter the full path to the bash script:
     `/home/YOUR_CPANEL_USERNAME/public_html/backend/scraper/cron_scraper.sh`
4. Click **Add New Cron Job**.

## 3. Verify Logs

The script will write output to `backend/scraper/scraper_cron.log`. 
You can check this file after the cron job runs to ensure it executed successfully and see if any URLs failed.
