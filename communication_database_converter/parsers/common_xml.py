from __future__ import annotations

from pathlib import Path
from typing import Iterable

from lxml import etree


def local_name(tag: str) -> str:
    return etree.QName(tag).localname if isinstance(tag, str) else ""


def text_of(element: etree._Element | None) -> str:
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def first_text(element: etree._Element, names: Iterable[str]) -> str:
    wanted = set(names)
    for child in element.iter():
        if local_name(child.tag) in wanted:
            value = text_of(child)
            if value:
                return value
    return ""


def parse_xml(path: Path) -> etree._ElementTree:
    parser = etree.XMLParser(recover=False, huge_tree=True, resolve_entities=False)
    return etree.parse(str(path), parser)


def iter_by_local_name(root: etree._Element, *names: str):
    wanted = set(names)
    for element in root.iter():
        if local_name(element.tag) in wanted:
            yield element
