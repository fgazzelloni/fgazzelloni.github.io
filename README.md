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
- 📻 Podcast episodes automatically fetched from Spotify

The website is built using [Quarto](https://quarto.org/), styled with custom CSS, and deployed via GitHub Pages.

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

## 📻 Automated Podcast Fetching

This repository includes an automated system that fetches new podcast episodes from Spotify daily and creates properly formatted blog posts. The system:

- Runs automatically every day at midnight UTC via GitHub Actions
- Fetches episodes from the [Health Metrics Show](https://open.spotify.com/show/43CSCODQFQkZ05u3Up5OD6) on Spotify
- Creates formatted Quarto markdown files for each new episode
- Downloads episode thumbnails
- Automatically commits and pushes new episodes to the repository

For more details on the podcast automation system, see [`scripts/README.md`](scripts/README.md).

### Manual Triggering

To manually fetch new podcast episodes:

1. Go to the [Actions tab](https://github.com/Fgazzelloni/fgazzelloni.github.io/actions)
2. Select "Fetch Podcast Episodes" workflow
3. Click "Run workflow" button
4. Confirm by clicking the green "Run workflow" button

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

🧭 For any questions or ideas for collaboration, feel free to reach out via LinkedIn or email me.
