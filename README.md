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

## Creating a Python Virtual Environment

1. **Create the virtual environment**:

    ```sh
    python3 -m venv myenv
    ```

2. **Activate the virtual environment**:

    - On macOS/Linux:

      ```sh
      source myenv/bin/activate
      ```

    - On Windows:

      ```sh
      .\myenv\Scripts\activate
      ```

3. **Confirm the Python version inside the virtual environment**:

    ```sh
    python --version
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
    pip install -r requirements.txt
    ```

## Running viptest.py

### Making viptest.py Executable

Ensure `viptest.py` is executable. You can either add it to your `$PATH` or call it directly. To make it executable:

```sh
chmod +x viptest.py
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

### Testing the Application

The repository includes a `testfile.csv` to run the initial test of the application. This can be tested with:

```sh
time unbuffer ./viptest.py --csv testfile.csv -c 50 > >(tee logfile1.log) 2>errors1.log
```

#### Explanation

- `time`: Measures the time taken to execute the command.
- `unbuffer`: Ensures that the output is not buffered, providing real-time output.
- `./viptest.py --csv testfile.csv -c 50`: Executes the script with the specified CSV file and concurrency level.
- `> >(tee logfile1.log)`: Redirects standard output to `logfile1.log` while also printing it to the terminal.
- `2>errors1.log`: Redirects standard error to `errors1.log`.

##### What's in logfile1.log?

`logfile1.log` contains the standard output of the script execution, which includes the results of the URL processing tests.

### Running Two Tests

First run:

```sh
time unbuffer ./viptest.py --csv testfile.csv -c 10 > >(tee logfile1.log) 2>errors1.log
```

Second run (after some change in the environment):

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
```

You can copy and paste this content into your `README.md` file in your GitHub repository. This format provides a comprehensive guide for setting up and running your `viptest.py` script.
