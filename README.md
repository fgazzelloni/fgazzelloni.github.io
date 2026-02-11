# Website

Welcome! This repository contains the source code and content for my personal website, built to share my work, teaching materials, ongoing projects, and thoughts on statistics, data science, and public health.

🔗 **Visit the site**: [federicagazzelloni.com](https://federicagazzelloni.com)

## 🚀 About

This site serves as a central hub for:

- 📘 My upcoming book: *Health Metrics and the Spread of Infectious Diseases* (CRC Press)
- 📊 R packages, code snippets, and reproducible analyses
- 🧪 Research on life expectancy, burden of disease, and machine learning in public health
- 🧑‍🏫 Workshops and materials from teaching and mentoring activities (Carpentries, Bioconductor, etc.)
- 💬 Talks, collaborations, and community events (R-Ladies, DSLC.io, etc.)

The website is built using [Quarto](https://quarto.org/), styled with custom CSS, and deployed via GitHub Pages.

## 🎙️ Automated Podcast Integration

This repository includes an automated system for fetching podcast episodes from Spotify and creating blog posts:

- **GitHub Actions workflow** runs daily to check for new episodes
- **R script** fetches episodes via Spotify API and generates Quarto posts
- Each episode gets its own formatted post with cover image
- Posts are automatically committed and published

For setup instructions, see [`scripts/README.md`](scripts/README.md) or [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md).

## 🛠️ How to Use or Contribute

If you're interested in contributing or adapting this site structure for your own work:

1. Clone the repo:
   ```bash
   git clone https://github.com/Fgazzelloni/federicagazzelloni.github.io.git
   ```
2.	Install Quarto if you haven’t already.
3.	Preview the site locally:
   ```bash
   quarto preview
   ```
4.	Customize content in the /posts, /projects, and _quarto.yml files.

Feel free to use this structure as a starting point for your own academic or professional site. Attribution is appreciated but not required. 

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

🧭 For any questions or ideas for collaboration, feel free to reach out via LinkedIn or email me.
