# VIPTest Usage Guide

This guide explains how to confirm the version of Python, create a virtual environment, install the necessary requirements, and run the `viptest.py` script. The repository is hosted at [https://github.com/tmarfil/viptest/tree/main](https://github.com/tmarfil/viptest/tree/main).

## Confirming Python Version

First, confirm that you have Python 3.8.x or later installed on your system.

```sh
python3 --version
```

If Python 3.8.x or later is installed, the output should be something like:

```
Python 3.8.10
```

## Installing Python3-venv and Pip3

- ### Red Hat-based Systems (e.g., RHEL, CentOS, Fedora):
  
  Update the package list
  
  ```bash
  sudo dnf update
  ```

  Enable the CodeReady Builder repository
  
  ```bash
  sudo dnf config-manager --set-enabled crb
  ```

  Install python3-virtualenv
  
  ```bash
  sudo dnf install python3-virtualenv
  ```

  Install pip3
  
  ```bash
  sudo dnf install python3-pip
  ```

- ### Debian-based Systems (e.g., Debian, Ubuntu):
  
  Update the package list
  
  ```bash
  sudo apt update
  ```
 
  Install python3-venv
  
  ```bash
  sudo apt install python3-venv
  ```
  
  Install pip3
  
  ```bash
  sudo apt install python3-pip
  ```
  
## Installing Complementary Linux Packages

VIPTest is Linux only. To install the complementary packages (time, diff, sort, tee, expect):
  
  - ### Red Hat-based Systems (e.g., RHEL, CentOS, Fedora):
    ```bash
    sudo dnf install time diffutils coreutils expect
    ```

  - ### Debian-based Systems (e.g., Debian, Ubuntu):
    ```bash
    sudo apt-get install time diffutils coreutils expect
    ```

The `coreutils` package includes `tee` and `sort` commands.

## Creating a Python Virtual Environment

1. **Create the virtual environment**:

    ```sh
    python3 -m venv myenv
    ```

2. **Activate the virtual environment**:

    ```sh
    source myenv/bin/activate
    ```

3. **Confirm the Python version inside the virtual environment**:

    ```sh
    python3 --version
    ```

    This should output the Python version being used in the virtual environment, e.g., `Python 3.8.10`.

## Installing Requirements

Install the required Python packages using the `requirements.txt` file hosted in the git repository.

1. **Clone the repository**:

    ```sh
    git clone https://github.com/tmarfil/viptest.git
    cd viptest
    ```

2. **Install the requirements**:

    ```sh
    pip3 install -r requirements.txt
    ```

## Running viptest.py

### Making viptest.py Executable

Ensure `viptest.py` is executable. You can either add it to your `$PATH` or call it directly. To make it executable:

```sh
sudo chmod +x viptest.py
```

### Usage of viptest.py

#### Simple Command

Run the script with the following command:

```sh
./viptest.py -c 10 --csv testfile.csv
```

#### Explanation

- `./viptest.py`: Executes the script.
- `-c 10`: Specifies the number of concurrent processes.
- `--csv testfile.csv`: Specifies the CSV file to use.

### Testing the Applications

The repository includes a `testfile.csv` to run tests against an example list of applications. This can be tested with:

```sh
time unbuffer ./viptest.py --csv testfile.csv -c 50 > >(tee logfile1.log) 2>errors1.log
```

#### Explanation

- `time`: Measures the time taken to execute the command.
- `unbuffer`: Ensures that the output is not buffered, providing real-time output.
- `./viptest.py --csv testfile.csv -c 50`: Executes the script with the specified CSV file and concurrency level.
- `> >(tee logfile1.log)`: Redirects standard output to `logfile1.log` while also printing it to the terminal.
- `2>errors1.log`: Redirects standard error to `errors1.log`.

##### Logfile Contents

`logfile1.log` contains the standard output of the script execution, which includes the results of the URL processing tests.

To quickly report on virtual servers that are not healthy:

```sh
cat logfile1.log | grep Error
```

Example output:

`[https://www.python.org] Error processing https://www.python.org: timed out`

### Running Two Tests

First run:

```sh
time unbuffer ./viptest.py --csv testfile.csv -c 10 > >(tee logfile1.log) 2>errors1.log
```

Next run (after some change in the environment):

```sh
time unbuffer ./viptest.py --csv testfile.csv -c 10 > >(tee logfile2.log) 2>errors2.log
```

### Comparing the Outputs

Sort the log files and compare the outputs to see what has changed:

1. **Sort the log files**:

    ```sh
    sort logfile1.log > sorted_logfile1.log && sort logfile2.log > sorted_logfile2.log
    ```

2. **Diff the sorted log files**:

    ```sh
    diff sorted_logfile1.log sorted_logfile2.log
    ```

### Explanation

- `sort logfile1.log > sorted_logfile1.log`: Sorts the contents of `logfile1.log` and writes it to `sorted_logfile1.log`.
- `diff sorted_logfile1.log sorted_logfile2.log`: Compares the sorted log files and outputs the differences.

## Configuration

### Editable Variables

The following variables can be adjusted within the `viptest.py` script:

- **USE_HTTP2**: Enables or disables HTTP/2 for HTTPS requests.
- **IGNORE_CERTIFICATE_WARNINGS**: Determines whether to ignore SSL certificate warnings.
- **MAX_CONCURRENCY**: Sets the maximum number of concurrent processes.
- **NAME_RESOLUTION_OVERRIDE**: Decides whether to use the IP address provided in the CSV file to override the system DNS resolution.

## Exiting a Python Virtual Environment

  > **Note: Exiting a Python Virtual Environment**
  >
  > To exit a Python virtual environment, simply run the `deactivate` command. This will deactivate the virtual environment and return you to your normal shell.
  >
  > ```sh
  > deactivate
  > ```
  >
  > Once you run this command, your shell prompt should no longer show the name of the virtual environment, indicating that you have successfully exited it.

# VIPTest CSV File Creation and Program Behavior

This guide explains how to create a CSV file for use with the `viptest.py` script and the expected behavior of the program. The CSV file consists of two columns: the first column is either a URL scheme or an IP address (with or without a port), and the second column contains an optional IP address.

## CSV File Format

The CSV file should have two columns:
1. **First Column**: URL scheme or IP address, with or without a port.
2. **Second Column**: Single IP address (optional).

### Example CSV File

Here is an example of a CSV file with five lines:

```csv
https://rudysbbq.com, 203.0.113.5
http://example.com, 192.0.2.1
192.168.50.50:23,
https://anotherexample.com:8443, 198.51.100.10
http://testsite.com,
```

### CSV File Entries Explained

1. **https://rudysbbq.com, 203.0.113.5**
   - **Behavior**: The program will report on the TLS version and ciphers and the response code from an HTTPS GET request to `https://rudysbbq.com`. The port defaults to 443 for HTTPS if none is specified.
   - **IP Override**: If `NAME_RESOLUTION_OVERRIDE = True`, the FQDN `rudysbbq.com` will resolve to the IP address `203.0.113.5` for the test.

2. **http://example.com, 192.0.2.1**
   - **Behavior**: The program will perform an HTTP GET request to `http://example.com` and report the response code. The port defaults to 80 for HTTP if none is specified.
   - **IP Override**: If `NAME_RESOLUTION_OVERRIDE = True`, the FQDN `example.com` will resolve to the IP address `192.0.2.1` for the test.

3. **192.168.50.50:23,**
   - **Behavior**: Since no HTTP or HTTPS scheme is specified, the program will ping the IP address `192.168.50.50` and check the status of port 23 (open or closed).

4. **https://anotherexample.com:8443, 198.51.100.10**
   - **Behavior**: The program will report on the TLS version and ciphers and the response code from an HTTPS GET request to `https://anotherexample.com:8443`.
   - **IP Override**: If `NAME_RESOLUTION_OVERRIDE = True`, the FQDN `anotherexample.com` will resolve to the IP address `198.51.100.10` for the test.

5. **http://testsite.com,**
   - **Behavior**: The program will perform an HTTP GET request to `http://testsite.com` and report the response code. The port defaults to 80 for HTTP if none is specified.
   - **IP Override**: No IP address is provided, so the program will use system DNS to resolve the FQDN.

6. **https://example.com/path/to/resource, 192.168.1.1**
   - **Behavior**: The program will report on the TLS version and ciphers and the response code from an HTTPS GET request to `https://example.com/path/to/resource`. The port defaults to 443 for HTTPS if none is specified.
   - **IP Override**: If `NAME_RESOLUTION_OVERRIDE = True`, the FQDN `example.com` will resolve to the IP address `192.168.1.1` for the test.

## Program Behavior Based on `NAME_RESOLUTION_OVERRIDE`

- **When `NAME_RESOLUTION_OVERRIDE = True`** (default):
  - The program will always override system DNS and resolve FQDNs in the first column to the IP address in the second column. This ensures consistent testing against the same Virtual Server / VIP in environments where an FQDN can resolve to multiple IP addresses or when testing an environment that is not yet resolvable via DNS.

- **When `NAME_RESOLUTION_OVERRIDE = False`**:
  - The program will rely on system DNS to resolve FQDNs in the first column and ignore the IP address in the second column.

By following these guidelines, you can create a CSV file that is compatible with the `viptest.py` script and understand how the program will behave based on the entries and configuration.

## Contributing

We welcome contributions to the VIPTest project. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact [tmarfil](https://github.com/tmarfil).

---

Thank you for using VIPTest!

