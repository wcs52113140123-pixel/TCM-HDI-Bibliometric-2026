# ============================================================
# Day 12 B — Block 4: Three-Field Plot + Thematic Map (v2)
# ============================================================
# v2 fixes vs initial draft:
#   - replace default thematicMap plot with custom ggrepel layout
#     (avoids label-corner overlap when only 2 of 4 quadrants are populated)
#   - correct quadrant assignment via rank-based median split
#     (rcentrality and rdensity are RANKS in 4.x, not 0-1 normalized)
#   - Q3 label y-offset +0.15 to clear descender clipping
# ============================================================

suppressPackageStartupMessages({
  library(bibliometrix)
  library(ggplot2)
  library(htmlwidgets)
})
if (!requireNamespace("ggrepel", quietly = TRUE)) install.packages("ggrepel")
library(ggrepel)

repo   <- "D:/Document/Research-Projects/TCM-HDI-Bibliometric-2026"
setwd(repo)
outdir <- "results/figures_bibliometrix"

M       <- readRDS(file.path(outdir, "M.rds"))
results <- readRDS(file.path(outdir, "biblio_results.rds"))
cat("Loaded M (", nrow(M), "rows) and biblio results\n\n")

# ============================================================
# 4.1 Three-Field Plot: country -> author -> keyword
# ============================================================
cat("=== Three-Field Plot ===\n")
tfp <- threeFieldsPlot(M,
                       fields = c("AU_CO", "AU", "DE"),
                       n      = c(20, 20, 30))
out_html <- file.path(outdir, "fig_threeFields_country_author_keyword.html")
htmlwidgets::saveWidget(
  tfp,
  file = normalizePath(out_html, mustWork = FALSE),
  selfcontained = TRUE)
cat(sprintf("Saved: %s (%.1f MB)\n",
            basename(out_html), file.size(out_html) / 1024 / 1024))
cat("For static PDF: open in Chrome -> Ctrl+P -> Save as PDF\n\n")

# ============================================================
# 4.2 Thematic Map
# ============================================================
cat("=== Thematic Map ===\n")
themat <- thematicMap(M,
                      field    = "ID",
                      n        = 250,
                      minfreq  = 5,
                      stemming = FALSE,
                      size     = 0.5,
                      n.labels = 3)

clu <- themat$clusters
cat("Clusters detected:", nrow(clu), "\n")

# ----- Correct quadrant assignment (rank-based median split) -----
mid_rc <- median(clu$rcentrality)
mid_rd <- median(clu$rdensity)
clu$quadrant <- with(clu, ifelse(
  rcentrality >  mid_rc & rdensity >  mid_rd, "Q1 Motor",
  ifelse(rcentrality <= mid_rc & rdensity >  mid_rd, "Q2 Niche",
  ifelse(rcentrality >  mid_rc & rdensity <= mid_rd, "Q4 Basic",
                                                     "Q3 Emerging"))))

write.csv(clu, file.path(outdir, "table_thematic_clusters.csv"),
          row.names = FALSE)
saveRDS(themat, file.path(outdir, "themat.rds"))

cat("\n=== Cluster summary ===\n")
print(clu[, c("name", "quadrant", "rcentrality", "rdensity", "freq", "n")])

# ----- Custom thematic map (replaces default themat$map) -----
okabe_ito <- c("#0072B2", "#D55E00", "#009E73", "#CC79A7")

pad <- 0.6
x_min <- min(clu$rcentrality) - pad
x_max <- max(clu$rcentrality) + pad
y_min <- min(clu$rdensity)    - pad
y_max <- max(clu$rdensity)    + pad

p_themat <- ggplot(clu, aes(x = rcentrality, y = rdensity)) +
  geom_hline(yintercept = mid_rd, linetype = "dashed", color = "grey55") +
  geom_vline(xintercept = mid_rc, linetype = "dashed", color = "grey55") +
  geom_point(aes(size = freq, fill = name),
             shape = 21, color = "white", alpha = 0.75, stroke = 0.6) +
  geom_label_repel(
    aes(label = name_full),
    size = 3.3, lineheight = 0.95,
    box.padding = 0.7, point.padding = 0.5,
    segment.color = "grey40", segment.size = 0.4,
    min.segment.length = 0.2,
    fill = scales::alpha("white", 0.92),
    color = "black", label.size = 0.3,
    seed = 42, max.overlaps = Inf
  ) +
  annotate("text", x = x_max, y = y_max, label = "Q1  Motor",
           color = "grey60", size = 3.4, hjust = 1, vjust = 1, fontface = "italic") +
  annotate("text", x = x_min, y = y_max, label = "Q2  Niche",
           color = "grey60", size = 3.4, hjust = 0, vjust = 1, fontface = "italic") +
  annotate("text", x = x_max, y = y_min, label = "Q4  Basic",
           color = "grey60", size = 3.4, hjust = 1, vjust = 0, fontface = "italic") +
  annotate("text", x = x_min, y = y_min + 0.15,
           label = "Q3  Emerging /\n     Declining",
           color = "grey60", size = 3.4, hjust = 0, vjust = 0,
           lineheight = 0.95, fontface = "italic") +
  scale_size_continuous(range = c(10, 28), guide = "none") +
  scale_fill_manual(values = okabe_ito, guide = "none") +
  scale_x_continuous(limits = c(x_min, x_max), expand = c(0, 0),
                     breaks = seq_len(max(clu$rcentrality))) +
  scale_y_continuous(limits = c(y_min, y_max), expand = c(0, 0),
                     breaks = seq_len(max(clu$rdensity))) +
  labs(
    title    = "Thematic structure of TCM-HDI literature (WoS subset)",
    subtitle = sprintf(
      "%d clusters from %d KeyWords Plus terms; Callon centrality-density (n = %d records)",
      nrow(clu), sum(clu$n), nrow(M)),
    x = "Centrality (rank)", y = "Density (rank)",
    caption = "Bubble area proportional to keyword frequency. Dashed lines: cluster-rank medians."
  ) +
  theme_minimal(base_size = 11) +
  theme(panel.grid.minor = element_blank(),
        panel.grid.major = element_line(color = "grey92"),
        plot.title       = element_text(face = "bold"),
        plot.subtitle    = element_text(color = "grey40", size = 9.5),
        plot.caption     = element_text(color = "grey55", size = 8, hjust = 0),
        axis.title       = element_text(color = "grey25"),
        plot.margin      = margin(t = 12, r = 16, b = 14, l = 12))

ggsave(file.path(outdir, "fig_thematicMap_keywords.pdf"),
       p_themat, width = 9, height = 6.5, device = cairo_pdf)
ggsave(file.path(outdir, "fig_thematicMap_keywords.png"),
       p_themat, width = 9, height = 6.5, dpi = 300, bg = "white")
cat("\nSaved fig_thematicMap_keywords.{pdf,png} (custom ggrepel layout)\n")
cat("\n=== Block 4 done ===\n")