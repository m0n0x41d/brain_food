import os
import typer
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from playwright.sync_api import sync_playwright
import textwrap

app = typer.Typer()
console = Console()


@app.command(name="get")
def get_kata(
    kata_link: str = typer.Argument(
        ...,
        help="Codewars kata URL link. The command will parse the title and problem, then create a directory with a Python module.",
        show_default=False,
    ),
) -> None:
    """
    Get kata from the provided Codewars URL and set up a submodule with Python files.
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(kata_link)

        page.wait_for_selector("#description")

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")

        if not soup:
            console.print(
                Panel(
                    "Failed to parse provided link",
                    title="ERROR",
                    border_style="red",
                )
            )
            raise SystemExit()

        title_element = soup.find("h4", class_="ml-2 mb-3")

        if not title_element:
            console.print(
                Panel(
                    "Failed to parse kata title on provided link page",
                    title="ERROR",
                    border_style="red",
                )
            )
            raise SystemExit()

        title = title_element.text.strip()
        description_div = soup.find("div", id="description")
        code_span = soup.find('span', role='presentation', style='padding-right: 0.1px;')
        code_snippet = ""
        func_name = ""
        if code_span:
            code_snippet = code_span.get_text(separator="\n").strip().splitlines()
            func_name = code_snippet[2]
            code_snippet = ''.join(code_snippet)

            
        else:
            console.print("Code Snippet not found.")

        if description_div:
            raw_description = description_div.get_text(separator="\n").strip()
            description_lines = clean_description(raw_description)
            description = format_description(description_lines)
        else:
            description = f"No description.\nRefer: '{kata_link}'"

        console.print("Kata Title:", title)
        console.print("Kata Description:\n", description)

        console.print("Going to create dir for you and bunch of python files...")

        dir_name = title.replace(" ", "_")
        dir_name = dir_name.lower()
        os.makedirs(dir_name, exist_ok=True)

        with open(f"{dir_name}/kata.py", "w") as f:
            f.write(f'"""{description}"""\n\n')
            f.write("# Your solution here\n")

        with open(f"{dir_name}/test_kata.py", "w") as f:
            f.write(f"from .kata import {func_name}\n\n")
            f.write(code_snippet)
            f.write(" "*4 + "# code something already")

        browser.close()


def clean_description(description: str) -> list[str]:
    lines = description.splitlines()
    filtered_lines = [line.strip() for line in lines if line.strip()]
    return filtered_lines


def format_description(description_lines, width=80):
    description = " ".join(description_lines)
    wrapped_description = textwrap.fill(description, width=width)
    return wrapped_description


if __name__ == "__main__":
    app()

