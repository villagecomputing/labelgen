# Superpipe - build, evaluate and optimize LLM pipelines

_A lightweight framework for building, evaluating and optimizing data transformation and data extraction pipelines using LLMs. Designed for simplicity, rapid prototyping, evaluation and optimization._

🚧 This readme and the docs are under construction 🚧

---

<p align="center">
  <a href="https://github.com/villagecomputing/superpipe">Star us on Github!</a> &nbsp; <a href="https://villagecomputing.github.io/superpipe/">Read the docs</a>
  <br><br>
  <a href="https://twitter.com/villagecompute"><img src="https://img.shields.io/twitter/follow/villagecompute?style=social"></a>
  <a href="https://pypi.python.org/pypi/superpipe-py"><img src="https://img.shields.io/pypi/dm/superpipe-py.svg"></a>
</p>

<p align="center"><img src="./docs/assets/superpipe_venn.png" style="width: 400px;" /></p>

LLMs can make your treasure trove of unstructured data useful if only you could transform it into structured, or extract key fields from it. Today, building LLM-powered pipelines is difficult because LLMs are unpredictable. Unlike traditional software, you can't simply write unit and integration tests that confirm the correctness of your code.

With LLMs you need a different approach: you need to evaluate your code on a dataset, and tune the code to find the right tradeoff between:

- Accuracy
- Cost
- Latency

Superpipe is an extremely lightweight framework that helps you build these pipelines such that you can:

- Easily run them on a dataset (not just a single data point)
- Keep track of token usage, cost and latency
- Evaluate accuracy against ground truth
- Evaluate the correctness of each step in the pipeline
- Easily parametrize each step (eg. model choice) so you can tune the parameters to optimize performance

## Get Started

Installing Superpipe is a breeze. Simply run `pip install superpipe-py` in your terminal.

## License

This project is licensed under the terms of the MIT License.

# Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

<a href="https://github.com/villagecomputing/superpipe/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=villagecomputing/superpipe" />
</a>
