# Federica Gazzelloni's Data Science Portfolio

Welcome! This repository powers my personal website — a dynamic portfolio showcasing my work at the intersection of **statistics, data science, and public health**.

🔗 **Visit the site**: [federicagazzelloni.com](https://federicagazzelloni.com)

---

## 🌟 About This Portfolio

This site is more than a personal homepage — it's a comprehensive **hub for health metrics, data science, and infectious disease research**. Here you'll find:

### 📘 Featured Book: *Health Metrics and the Spread of Infectious Diseases*

My book with **CRC Press** explores quantitative methods for analyzing disease spread and health outcomes. The website includes:

- Dedicated **Books** section with resources and updates
- **hmsidwR** R package documentation and tutorials
- Companion materials, code examples, and case studies

### 📊 R Packages & Code

- **hmsidwR**: Health metrics tools for infectious disease analysis
- **oregonfrogs**: Ecological data analysis utilities
- **typeR**: Typography and text analysis tools
- Reproducible analyses, tutorials, and package documentation

### 🧪 Research & Projects

- Life expectancy modeling and burden of disease studies
- Machine learning applications in public health
- Performance metrics and impact analysis
- Data-driven insights from epidemiological research

### 🎙️ Podcasts

Automated integration with my **Spotify podcast** featuring discussions on:

- Health metrics and infectious disease research
- Data science methodologies
- Public health innovations
- Interviews with researchers and practitioners

### 🧑‍🏫 Teaching & Community

Materials from my work with:

- **The Carpentries** (data science workshops)
- **Bioconductor** (genomic data analysis)
- **R-Ladies** and **DSLC.io** (community building and mentoring)
- Conference talks, workshops, and training sessions

---

## 🎙️ Automated Podcast Integration

A unique feature of this portfolio is the **automated podcast episode publishing system**:

### How It Works

- 🤖 **GitHub Actions workflow** runs daily to fetch new episodes from Spotify
- 📝 **R script** (`scripts/fetch-podcasts.R`) automatically generates formatted blog posts
- 🎨 Each episode gets its own page with cover art, embedded player, and key topics
- ⚡ New episodes are committed and published automatically

### Quick Start

To enable podcast automation:

1. **Get Spotify API credentials** from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. **Add GitHub Secrets**: `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
3. **Configure the show ID** in `scripts/fetch-podcasts.R`
4. **Run manually** via Actions tab, or wait for the daily automatic run

For detailed setup instructions, see:

- [`scripts/README.md`](scripts/README.md) — Complete automation documentation
- [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) — Technical implementation details

---

## 🏗️ Built With

- **[Quarto](https://quarto.org/)** — Scientific and technical publishing system
- **R & RStudio** — Statistical computing and package development
- **GitHub Pages** — Hosting and continuous deployment
- **GitHub Actions** — Automated workflows for content updates
- **Custom CSS** — Tailored design and responsive layouts

---

## 🚀 Getting Started

### For Visitors
Simply visit [federicagazzelloni.com](https://federicagazzelloni.com) to explore the content!

### For Contributors or Developers

Want to adapt this structure for your own portfolio? Here's how:

1. **Clone the repository**
   ```bash
   git clone https://github.com/Fgazzelloni/fgazzelloni.github.io.git
   cd fgazzelloni.github.io
   ```

2. **Install Quarto**
   Download from [quarto.org](https://quarto.org/docs/get-started/)

3. **Preview locally**
   ```bash
   quarto preview
   ```

4. **Customize content**
   - Edit site structure in `_quarto.yml` and `_website.yml`
   - Add blog posts in `content/blog/posts/`
   - Modify R package docs in `content/rpackages/`
   - Update project showcases in `content/proj/`

5. **Deploy**
   - Push to `main` branch
   - GitHub Actions will build and deploy automatically

---

## 📂 Repository Structure

```
.
├── content/
│   ├── blog/          # Data visualization & analytics posts
│   ├── books/         # HMSIDwR book resources
│   ├── podcasts/      # Automated podcast episodes
│   ├── proj/          # Project showcases
│   └── rpackages/     # R package documentation
├── scripts/
│   └── fetch-podcasts.R   # Spotify automation
├── .github/workflows/
│   └── fetch-podcasts.yml # Daily automation workflow
├── _quarto.yml        # Quarto project configuration
├── _website.yml       # Website structure & navigation
└── about.qmd          # About page
```

---

## 🤝 Contributing

This is a personal portfolio, but I welcome:
- 🐛 **Bug reports** for technical issues
- 💡 **Suggestions** for improvements
- 🔗 **Collaboration ideas** on research or teaching projects

Feel free to [open an issue](https://github.com/Fgazzelloni/fgazzelloni.github.io/issues) or reach out directly!

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE.md) file for details.

You're welcome to use this structure as inspiration for your own site. Attribution is appreciated but not required!

---

## 📬 Connect With Me

- 💼 [LinkedIn](https://www.linkedin.com/in/federicagazzelloni/)
- 📧 [Email](mailto:fede.gazzelloni@gmail.com)
- 🐙 [GitHub](https://github.com/fgazzelloni)
- 📰 [Substack](https://federicagazzelloni.substack.com/)
- 🦋 [Bluesky](https://bsky.app/profile/fgazzelloni.bsky.social)
- 🐦 [Twitter/X](https://x.com/FGazzelloni)
- 🎓 [Google Scholar](https://scholar.google.com/citations?hl=en&user=Xes0-r0AAAAJ)
- 🔬 [ORCID](https://orcid.org/0000-0002-4285-611X)

---

<p align="center">
  <em>Built with 💜 using Quarto and R</em><br>
  <em>Automated with GitHub Actions</em><br>
  <em>Dedicated to advancing health metrics and data science</em>
</p>