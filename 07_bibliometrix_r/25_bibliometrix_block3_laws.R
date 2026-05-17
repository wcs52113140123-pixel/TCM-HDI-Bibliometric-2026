# ============================================================
# Day 12 B — Block 3: Lotka's Law + Bradford's Law (v2, 4.x compatible)
# ============================================================
# v2 fixes vs initial draft:
#   - lotka(M) signature (not lotka(results)) per bibliometrix 4.x
#   - L$AuthorProd column names: "Documents written" / "N. of Authors"
#     -> rename to safe names before downstream ops
#   - Bradford section uses bibliometrix's built-in Rank/cumFreq cols
# ============================================================
# Input:  results/figures_bibliometrix/M.rds + biblio_results.rds
# Output:
#   - figS_alt_lotka.{pdf, png}        (Day 3 figure_06b alternative)
#   - figS_alt_bradford.{pdf, png}     (Day 3 figure_07b alternative)
#   - table_lotka_fit.csv
#   - table_bradford_zones.csv
# ============================================================

suppressPackageStartupMessages({
  library(bibliometrix)
  library(ggplot2)
})

repo   <- "D:/Document/Research-Projects/TCM-HDI-Bibliometric-2026"
setwd(repo)
outdir <- "results/figures_bibliometrix"

M       <- readRDS(file.path(outdir, "M.rds"))
results <- readRDS(file.path(outdir, "biblio_results.rds"))
cat("Loaded M (", nrow(M), "rows) and biblio results\n\n")

# ============================================================
# Lotka's Law (bibliometrix 4.x: lotka takes M, not results)
# ============================================================
cat("=== Lotka's Law fit ===\n")
L <- lotka(M)
cat(sprintf("  Beta (Lotka alpha)  : %.3f\n", L$Beta))
cat(sprintf("  C (constant)        : %.3f\n", L$C))
cat(sprintf("  R^2 (fit quality)   : %.3f\n", L$R2))
cat(sprintf("  p-value (vs 2.0)    : %.4f\n", L$p.value))

# Save params (with Python D2 reference)
lotka_df <- data.frame(
  metric    = c("alpha (Beta)", "C (constant)", "R^2", "p-value (vs 2.0)"),
  value     = c(L$Beta, L$C, L$R2, L$p.value),
  python_d2 = c(2.63, NA, 0.957, NA)
)
write.csv(lotka_df, file.path(outdir, "table_lotka_fit.csv"),
          row.names = FALSE)

# bibliometrix 4.x L$AuthorProd cols: "Documents written" / "N. of Authors" / "Proportion of Authors"
ap <- L$AuthorProd
colnames(ap)[1:3] <- c("Articles", "NAuthors", "Prop")
ap$Articles <- as.numeric(ap$Articles)
ap$NAuthors <- as.numeric(ap$NAuthors)
ap$prop     <- ap$NAuthors / sum(ap$NAuthors)

p_lotka <- ggplot(ap, aes(x = Articles, y = prop)) +
  geom_point(color = "#0072B2", size = 2.2, alpha = 0.85) +
  geom_smooth(method = "lm", formula = y ~ x, se = FALSE,
              color = "#D55E00", linewidth = 0.8, linetype = "dashed") +
  scale_x_log10() + scale_y_log10() +
  labs(
    title    = "Author productivity (Lotka's Law) — WoS subset",
    subtitle = sprintf(
      "n = %d authors; alpha = %.2f, R^2 = %.3f  |  Python D2: alpha = 2.63, R^2 = 0.957",
      results$nAuthors, L$Beta, L$R2),
    x = "Articles per author (log)", y = "Proportion of authors (log)"
  ) +
  theme_minimal(base_size = 11) +
  theme(panel.grid.minor = element_blank(),
        plot.title       = element_text(face = "bold"),
        plot.subtitle    = element_text(color = "#444", size = 9.5))

ggsave(file.path(outdir, "figS_alt_lotka.pdf"),
       p_lotka, width = 7, height = 4.5, device = cairo_pdf)
ggsave(file.path(outdir, "figS_alt_lotka.png"),
       p_lotka, width = 7, height = 4.5, dpi = 300, bg = "white")
cat("Saved figS_alt_lotka.{pdf,png}\n\n")

# ============================================================
# Bradford's Law (bibliometrix 4.x: btab has SO/Rank/Freq/cumFreq/Zone)
# ============================================================
cat("=== Bradford's Law zones ===\n")
B    <- bradford(M)
btab <- B$table
cat(sprintf("  Total journals : %d\n", nrow(btab)))

zone_counts <- table(btab$Zone)
cat("  Zone counts:\n")
print(zone_counts)

nz <- as.integer(zone_counts)
m1 <- nz[2] / nz[1]
m2 <- nz[3] / nz[2]
mg <- sqrt(m1 * m2)
cat(sprintf("  Z1->Z2 multiplier : %.2f\n", m1))
cat(sprintf("  Z2->Z3 multiplier : %.2f\n", m2))
cat(sprintf("  Geometric mean    : %.2f  |  Python D2: 8.89\n", mg))

cat("\n  Zone 1 core journals:\n")
core <- btab[btab$Zone == "Zone 1", c("SO", "Freq", "Rank", "Zone")]
print(core)

# Save full zones table
write.csv(btab, file.path(outdir, "table_bradford_zones.csv"),
          row.names = FALSE)

# Bradford plot using bibliometrix's native Rank and cumFreq
btab$cumProp <- btab$cumFreq / sum(btab$Freq)
z1_idx <- max(btab$Rank[btab$Zone == "Zone 1"])
z2_idx <- max(btab$Rank[btab$Zone == "Zone 2"])

p_brad <- ggplot(btab, aes(x = Rank, y = cumProp, color = Zone)) +
  geom_line(linewidth = 0.9) +
  geom_vline(xintercept = c(z1_idx, z2_idx),
             linetype = "dotted", color = "#666666") +
  scale_x_log10() +
  scale_y_continuous(labels = scales::percent) +
  scale_color_manual(values = c("Zone 1" = "#0072B2",
                                "Zone 2" = "#E69F00",
                                "Zone 3" = "#999999")) +
  labs(
    title    = "Bradford's Law of scattering (WoS subset)",
    subtitle = sprintf(
      "Total journals: %d  |  Zone sizes: %d / %d / %d  |  multiplier = %.2f (Python D2: 8.89)",
      nrow(btab), nz[1], nz[2], nz[3], mg),
    x = "Journal rank (log scale)", y = "Cumulative share of articles"
  ) +
  theme_minimal(base_size = 11) +
  theme(panel.grid.minor = element_blank(),
        plot.title       = element_text(face = "bold"),
        plot.subtitle    = element_text(color = "#444", size = 9.5),
        legend.position  = "right")

ggsave(file.path(outdir, "figS_alt_bradford.pdf"),
       p_brad, width = 7.5, height = 4.5, device = cairo_pdf)
ggsave(file.path(outdir, "figS_alt_bradford.png"),
       p_brad, width = 7.5, height = 4.5, dpi = 300, bg = "white")
cat("\nSaved figS_alt_bradford.{pdf,png}\n")
cat("\n=== Block 3 done ===\n")