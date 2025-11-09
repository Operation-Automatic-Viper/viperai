# ViperAI

<div align="center">
  <a href="#">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">ViperAI</h3>

  <p align="center">
    A simple RED TEAMING agent to help you with your pentest!
    <br />
    <a href="#"><strong>Explore the docs</strong></a>
    <br />
    <br />
    <a href="https://github.com/">View Demo</a>
    ·
    <a href="email:rayenguedria12@gmail.com">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

ViperAI is an autonomous pentester AI agent designed to assist with red teaming and penetration testing. It plans, executes security scans, checks for vulnerabilities, and self-improves through reflection. Built with Scrum methodology, it features a modular architecture for tools like CHAOS, Nikto, and CVE lookup.

Here's why ViperAI is useful:
* Automates pentesting workflows with self-reasoning (chain-of-thought).
* Supports resume from crashes and human-in-the-loop approvals for sensitive actions.
* Focuses on safety: sandboxed tools, no auto-run exploits.
* Extensible with plugin system for new tools.

This project follows a Scrum roadmap with 5 sprints, starting from core planning to professional reporting.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python]][Python-url]
* [![OpenAI][OpenAI]][OpenAI-url]
* [![Poetry][Poetry]][Poetry-url]
* [![Subprocess][Subprocess]][Subprocess-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get ViperAI running locally, follow these steps.

### Prerequisites

* Python 3.11+
* Poetry (dependency manager): Install with `curl -sSL https://install.python-poetry.org | python3 -`
* OpenAI API Key: Sign up at [OpenAI](https://platform.openai.com/account/api-keys)
* CHAOS tool: Install with `go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest`

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/your_username/viperai.git
   ```
2. Navigate to the project directory
   ```sh
   cd viperai
   ```
3. Install dependencies with Poetry
   ```sh
   poetry install
   ```
4. Set your OpenAI API Key
   ```sh
   export OPENAI_API_KEY='sk-your-api-key'
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Run a scan:
```sh
poetry run viperai scan example.com
```

Resume a session:
```sh
poetry run viperai resume sessions/viperai_session_20251109.json
```

For more details, see the [Documentation](https://example.com).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Sprint 1: Core planning, CHAOS tool, resume
- [ ] Sprint 2: Nikto adapter, reflection loop
- [ ] Sprint 3: Multi-source fingerprinting (Wappalyzer, TLS, crt.sh)
- [ ] Sprint 4: CVE lookup, risk scoring, /approve gate
- [ ] Sprint 5: Reporting (PDF), unit tests

See the [open issues](https://github.com/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are welcome! To contribute:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Rayen Guedria - [@your_twitter](https://twitter.com/your_username) - rayenguedria12@gmail.com

Oussama - oussama@example.com

Project Link: [https://github.com/your_username/viperai](https://github.com/your_username/viperai)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [OpenAI API](https://openai.com)
* [ProjectDiscovery (CHAOS)](https://github.com/projectdiscovery/chaos-client)
* [Poetry](https://python-poetry.org)
* [Best README Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[OpenAI]: https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white
[OpenAI-url]: https://openai.com/
[Poetry]: https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white
[Poetry-url]: https://python-poetry.org/
[Subprocess]: https://img.shields.io/badge/Subprocess-000000?style=for-the-badge&logo=python&logoColor=white
[Subprocess-url]: https://docs.python.org/3/library/subprocess.html