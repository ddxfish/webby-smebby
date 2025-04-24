# Webby - Website Uptime Checker

Webby is a desktop application for monitoring website uptime and availability. Built with PyQt5, it provides a clean, intuitive interface to track the status of multiple websites simultaneously. Webby performs comprehensive health checks including DNS resolution, SSL certificate validation, HTTP response codes, and content validation, allowing you to quickly identify and respond to outages.

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
A: Yes, all status changes are logged to an SQLite database, including timestamps, status codes, and error details.

**Q: How does Webby minimize network overhead?**  
A: Webby uses a tiered checking system, first attempting DNS resolution, then SSL validation, and only then making HTTP requests. This prevents unnecessary network traffic for sites with fundamental connectivity issues.

**Q: Can I run Webby in the background?**  
A: Yes, Webby is designed to be lightweight and can run continuously in the background, alerting you when issues arise.

**Q: How does Webby handle slow-responding websites?**  
A: Connection timeouts are set to 10 seconds by default to accommodate slower websites while preventing the application from hanging indefinitely.

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
