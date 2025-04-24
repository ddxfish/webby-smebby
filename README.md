# Webby - Website Uptime Checker

Webby is a desktop application for monitoring website uptime and availability. Built with PyQt5, it provides a straightforward interface to track the status of multiple websites. It performs basic health checks including DNS resolution, SSL certificate validation, HTTP response codes, and content validation, helping you identify potential website issues. While suitable for digital signage and personal monitoring, it's not intended to replace dedicated enterprise-level uptime services.

![image](https://github.com/user-attachments/assets/5f06cc62-b307-49f7-810d-46676efc846f)

## Features

- **Real-time monitoring** of website availability and uptime
- **Multi-level health checks**: DNS, SSL, HTTP, and content string validation
- **Visual status indicators** showing current health state
- **Time tracking** for last seen and last failure events
- **CSV import/export** for easy backup and migration
- **Customizable check frequency** to balance monitoring needs with system resources
- **Dark/light theme support** for comfortable viewing in any environment
- **Low resource footprint** suitable for continuous background operation
- **Watchdog monitoring** to ensure application stability and prevent UI freezes
- **Graceful error recovery** with emergency state saving
- **Threaded website checking** for improved performance and reliability
- **Auto-pruning of old logs** to maintain database efficiency

## Installation

### Prerequisites
- Python 3.6+
- PyQt5
- dnspython

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/ddxfish/webby-smebby.git
   cd webby
   ```

2. Install required dependencies:
   ```
   pip install PyQt5 dnspython
   ```

3. Run the application:
   ```
   python main.py
   ```

## Usage

### Adding Websites
1. Click on "Edit" > "Add Site" or use the corresponding menu option
2. Enter a friendly name, URL, and optional content string to check for
3. Click "OK" to begin monitoring

### Configuration
- Access settings through "Settings" > "Settings"
- Adjust check frequency, toggle specific check types (DNS, SSL, HTTP, string)
- Switch between light and dark theme

### Monitoring
- The main table displays all monitored websites with their current status
- Status icons in the header and status bar indicate overall system health
- Last failure details are displayed in the status bar

## Technical Q&A

**Q: How frequently does Webby check websites by default?**  
A: By default, Webby checks websites every 300 seconds (5 minutes). This can be adjusted in the settings.

**Q: Does Webby keep a history of status changes?**  
A: Yes, all status changes are logged to an SQLite database, including timestamps, status codes, and error details. The application automatically prunes logs older than 30 days to maintain database efficiency.

**Q: How does Webby minimize network overhead?**  
A: Webby uses a tiered checking system, first attempting DNS resolution, then SSL validation, and only then making HTTP requests. This prevents unnecessary network traffic for sites with fundamental connectivity issues.

**Q: Can I run Webby in the background?**  
A: Yes, Webby is designed to be lightweight and can run continuously in the background, alerting you when issues arise.

**Q: How does Webby handle slow-responding websites?**  
A: Connection timeouts are set to 10 seconds by default for HTTP connections. The overall check timeout is dynamically set to half of the configured check frequency (with a maximum of 30 seconds) to prevent checks from overlapping while still allowing for slower websites.

**Q: What happens if a website check gets stuck?**  
A: Each website check runs in its own thread with a timeout mechanism. If a check exceeds the timeout limit, it's marked as failed with a "Timeout" status without affecting other checks or freezing the application.

**Q: What is the UI watchdog feature?**  
A: Webby includes a basic UI watchdog that monitors application responsiveness. If the UI becomes unresponsive, the watchdog tries to recover it or perform a clean shutdown. This helps reduce the chance of completely frozen interfaces but isn't foolproof - occasional manual restarts may still be necessary with prolonged use.

**Q: Does Webby attempt to protect against data loss?**  
A: Webby attempts to save your website list during unexpected shutdowns, but this emergency feature is a best-effort mechanism and not guaranteed to work in all crash scenarios. Regular manual exports are recommended for important configurations.

**Q: How does the threaded checking system improve reliability?**  
A: By running each website check in its own thread, a single slow or problematic website won't block checks of other websites. This architecture also allows for graceful cancellation of ongoing checks when needed, such as during application shutdown.

**Q: Can I run Webby with a launcher for improved reliability?**  
A: Webby includes a basic launcher script that can restart the application if it crashes, which helps with reliability for a desktop tool. However, it lacks features of professional monitoring services like redundant checking from multiple locations, SMS alerts, or guaranteed uptime.

**Q: How does Webby compare to professional uptime monitoring services?**  
A: Webby is a lightweight desktop tool suitable for basic monitoring needs or digital signage displays. Professional services offer geographical redundancy, SLA guarantees, advanced alerting systems, and historical reporting that Webby doesn't provide. Choose Webby for personal projects or internal status boards, but consider dedicated services for business-critical websites.

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.