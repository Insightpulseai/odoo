"""
InsightPulseAI Platform SDK - Python
Phase 5B: SaaS Platform Kit - SDK Creation
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ipai-ai-sdk",
    version="0.1.0",
    author="InsightPulseAI",
    author_email="business@insightpulseai.com",
    description="InsightPulseAI Platform SDK - AI services client for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Insightpulseai/odoo",
    project_urls={
        "Bug Tracker": "https://github.com/Insightpulseai/odoo/issues",
        "Documentation": "https://insightpulseai.com/docs/platform/ai",
        "Source Code": "https://github.com/Insightpulseai/odoo/tree/main/packages/ipai-ai-sdk-python",
    },
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=0.990",
            "types-requests>=2.25.0",
        ],
    },
    keywords="ai rag supabase openai insightpulseai platform sdk",
    license="MIT",
)
