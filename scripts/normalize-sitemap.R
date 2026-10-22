sitemap <- file.path("_site", "sitemap.xml")

if (file.exists(sitemap)) {
  lines <- readLines(sitemap, warn = FALSE)
  lines <- gsub("/index[.]html</loc>", "/</loc>", lines)
  # Incremental renders can retain both / and /index.html entries.
  # After canonicalising them, keep the latest occurrence of each URL.
  starts <- which(trimws(lines) == "<url>")
  ends <- which(trimws(lines) == "</url>")
  if (length(starts) == length(ends) && length(starts) > 0) {
    locations <- vapply(seq_along(starts), function(i) {
      block <- lines[starts[i]:ends[i]]
      sub(".*<loc>(.*)</loc>.*", "\\1", block[grepl("<loc>", block)][1])
    }, character(1))
    repeated <- which(duplicated(locations, fromLast = TRUE))
    if (length(repeated) > 0) {
      remove <- unlist(lapply(repeated, function(i) starts[i]:ends[i]))
      lines <- lines[-remove]
    }
  }
  writeLines(lines, sitemap, useBytes = TRUE)
}

homepage <- file.path("_site", "index.html")

if (file.exists(homepage)) {
  lines <- readLines(homepage, warn = FALSE)

  if (!any(grepl("class=\"pagination\"", lines, fixed = TRUE))) {
    lines <- lines[!grepl("pagination: { item:", lines, fixed = TRUE)]
    writeLines(lines, homepage, useBytes = TRUE)
  }
}
