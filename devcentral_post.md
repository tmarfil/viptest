# VIPTest: Rapid Application Testing for F5 Environments

## The Motivation Behind VIPTest

As an F5 Solutions Architect, I noticed a recurring challenge with prospective customers: there was no quick way to "grade" the success of migrating from their current environment to F5 solutions. This gap made it difficult to quickly identify and address problem areas. To solve this, I developed [VIPTest](https://github.com/tmarfil/viptest) - a tool designed as a convenience for anyone considering moving their applications from a different vendor solution (e.g., Citrix NetScaler) to F5.

However, VIPTest's utility extends far beyond migration scenarios. It can be used in any environment where you introduce a change and need an automated process to assess the success of these changes. Whether you're upgrading software, modifying configurations, or performing routine maintenance, VIPTest provides a rapid, comprehensive snapshot of your application landscape.

## F5's Application Services and Security Solutions

Before we dive into VIPTest, let's briefly explore F5's three new families of Application Services and Security solutions:

1. [F5 Distributed Cloud (XC)](https://www.f5.com/cloud): A SaaS-based security, networking, and application management solution that provides multi-cloud networking, web application and API protection, and edge-based computing.

2. [BIG-IP Next](https://www.f5.com/products/big-ip-services/big-ip-next): The next generation of F5's flagship product, offering advanced traffic management, security, and analytics in a more flexible, software-first architecture.

3. [NGINX](https://www.nginx.com/): A suite of cloud native technologies that provide API gateway, reverse proxy, and application security, known for its high performance and scalability.

With VIPTest, you can confidently introduce changes to any of these solutions and quickly assess their impact. It's equally valuable for evaluating initial migrations and for ongoing operational changes within the same solution.

## The Problem VIPTest Solves

Customers often lack a quick, automated way to assess the impact of environment changes on their applications. VIPTest addresses this by providing:

1. Fast, concurrent testing of multiple URLs
2. Pre and post-change comparisons
3. Detection of improvements (e.g., TLS upgrades, HTTP/1.1 to HTTP/2 upgrades) and issues (e.g., broken connectivity)
4. Identification of deprecated applications so you don't wast time testing 'dead' URLs
5. Rapid assessment when migrating from another vendor's solution, such as Citrix NetScaler
6. A simple mechanism to target _just_ a staging environment during testing by overriding system DNS with static IP entries

Let's explore how VIPTest works and how you can leverage it in your F5 environment.

## How VIPTest Works

VIPTest, available on [GitHub](https://github.com/tmarfil/viptest), accepts a CSV file containing URLs and IP addresses. It then:

1. Validates URLs and IP addresses
2. Performs HTTP/HTTPS requests
3. Checks TLS versions and ciphers
4. Tests connectivity (ping and telnet)
5. Reports results for easy comparison


## Key Features

1. **Concurrent Processing**: VIPTest uses Python's multiprocessing module to test as many URLs simultaneously as your client machine can support. On my modest Intel 10th gen / 6 Core laptop, I can test 1000 URLs in less than one minute.

2. **Flexible URL Handling**: It supports various URL formats, including:
   - Full URLs (http://example.com)
   - IP addresses with ports (192.168.1.1:80)
   - URLs with custom ports (https://example.com:8443)

3. **Detailed Reporting**: VIPTest provides information on:
   - HTTP response codes
   - TLS versions and ciphers
   - IP resolution
   - Connectivity status

VIPTest works with Linux, Windows ([WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)), or MacOS ([Zsh using homebrew](https://brew.sh)).

## Setting Up VIPTest

See [README.md](https://github.com/tmarfil/viptest/tree/main) for full installation and useage details.

1. Ensure you have Python 3.8+ installed:

   ```
   python3 --version
   ```

2. Create a virtual environment:

   ```
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. Clone the VIPTest repository:

   ```
   git clone https://github.com/tmarfil/viptest.git
   cd viptest
   ```

4. Install requirements:

   ```
   pip3 install -r requirements.txt
   ```

5. Make viptest.py executable:

   ```
   chmod +x viptest.py
   ```

## Using VIPTest

1. Create a CSV file with your URLs (see README.md for format details).

2. Run VIPTest:

   ```
   viptest.py --csv your_file.csv -c 50
   ```

   This tests URLs concurrently using 50 processes.

3. Save the output:

   ```
   viptest.py --csv your_file.csv -c 50 > pre_change_results.log
   ```

4. Make your environment changes.

5. Run VIPTest again:

   ```
   viptest.py --csv your_file.csv -c 50 > post_change_results.log
   ```

6. Compare results:

   ```
   diff pre_change_results.log post_change_results.log
   ```

## The Power of HTTPX

VIPTest leverages the [HTTPX client for Python3](https://www.python-httpx.org/):

1. HTTP/2 Support: Enables testing of modern application stacks.
2. Automatic Retries: Improves reliability in unstable network conditions.
3. Connection Pooling: Enhances performance for multiple requests to the same host.
4. Timeout Handling: Prevents hung requests from slowing down the entire test suite.

## Concurrent Testing with Multiprocessing

The [Python multiprocessing package](https://docs.python.org/3/library/multiprocessing.html) is crucial for VIPTest's performance. Here's how it works:

1. The URL list is divided into chunks.
2. Each chunk is processed by a separate Python process.
3. Results are collected in a shared queue.

This approach allows VIPTest to test one thousand URLs in less than one minute. The Python code implements this using:

```python
if args.concurrent:
    chunk_size = len(urls) // args.concurrent
    chunks = list(chunked_iterable(urls, chunk_size))
    processes = []
    for chunk in chunks:
        p = multiprocessing.Process(target=process_urls, args=(chunk, output_queue, counter))
        processes.append(p)
        p.start()
```

## Automating with CI/CD

Integrating VIPTest into your CI/CD pipeline ensures consistent testing. Here's a basic GitHub Actions workflow:

```yaml
name: VIPTest

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run VIPTest
      run: |
        viptest.py --csv testfile.csv -c 50 > test_results.log
    - name: Upload results
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: test_results.log
```

This workflow runs VIPTest on every push to the main branch or pull request, saving the results as an artifact.

For GitLab users, a similar pipeline can be created using .gitlab-ci.yml:

```yaml
stages:
  - test

viptest:
  stage: test
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - viptest.py --csv testfile.csv -c 50 > test_results.log
  artifacts:
    paths:
      - test_results.log
```

## Conclusion

VIPTest empowers F5 customers to confidently make environment changes across all F5 solutions - from Distributed Cloud (XC) to BIG-IP Next and NGINX. By providing quick, comprehensive application testing, it reduces risk and improves the success rate of migrations, upgrades, and day-to-day operations. Whether you're moving from a competitor's solution or optimizing your current F5 setup, VIPTest is an invaluable tool in your toolkit.

Start using [VIPTest](https://github.com/tmarfil/viptest) today to ensure your applications stay healthy through every environment change!
