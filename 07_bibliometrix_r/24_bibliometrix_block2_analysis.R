# ============================================================
# Day 12 B — Block 2: biblioAnalysis + Fig 2 alt + top tables
# ============================================================
# Input:  results/figures_bibliometrix/M.rds (3091 WoS records)
# Output:
#   - biblio_results.rds (full analysis object, for next blocks)
#   - fig2_alt_annual_production.{pdf, png}
#   - fig2_alt_avg_citations_per_article.{pdf, png}
#   - table_bibliometrix_top_{sources, authors, countries,
#     cited_papers}.csv  (top-20 each for paper supplementary)
# ============================================================

suppressPackageStartupMessages({
  library(bibliometrix)
  library(ggplot2)
})

repo   <- "D:/Document/Research-Projects/TCM-HDI-Bibliometric-2026"
setwd(repo)
outdir <- "results/figures_bibliometrix"

# Load M from Block 1
M <- readRDS(file.path(outdir, "M.rds"))
cat("Loaded M:", nrow(M), "rows x", ncol(M), "cols\n\n")

# ---- biblioAnalysis (heavy step, expect 30-60s) ----
cat("Running biblioAnalysis...\n")
t0 <- Sys.time()
results <- biblioAnalysis(M, sep = ";")
cat("biblioAnalysis elapsed:",
    round(as.numeric(difftime(Sys.time(), t0, units = "secs")), 1),
    "sec\n\n")

saveRDS(results, file.path(outdir, "biblio_results.rds"))

# ---- Compact summary stats ----
cat("=== Main information (WoS subset) ===\n")
cat(sprintf("  Documents          : %d\n", nrow(M)))
cat(sprintf("  Sources (journals) : %d\n", length(unique(M$SO))))
cat(sprintf("  Authors            : %d\n", results$nAuthors))
cat(sprintf("  Author appearances : %d\n", results$Appearances))
cat(sprintf("  Multi-author docs  : %d\n", results$AuMultiAuthoredArt))
cat(sprintf("  Years              : %d - %d\n",
            min(M$PY, na.rm = TRUE), max(M$PY, na.rm = TRUE)))
cat(sprintf("  Total citations    : %d\n",
            sum(as.numeric(M$TC), na.rm = TRUE)))
cat(sprintf("  Avg cit / doc      : %.2f\n",
            mean(as.numeric(M$TC), na.rm = TRUE)))
cat("\n")

# ---- Generate bibliometrix default plots ----
cat("Generating bibliometrix default plot list...\n")
P <- plot(x = results, k = 20, pause = FALSE)
cat("Plot list contents:\n")
print(names(P))
cat("\n")

# ---- Save Fig 2 alt: annual scientific production ----
if (!is.null(P$AnnualScientProd)) {
  ggsave(file.path(outdir, "fig2_alt_annual_production.pdf"),
         plot = P$AnnualScientProd,
         width = 7, height = 4, device = cairo_pdf)
  ggsave(file.path(outdir, "fig2_alt_annual_production.png"),
         plot = P$AnnualScientProd,
         width = 7, height = 4, dpi = 300, bg = "white")
  cat("Saved: fig2_alt_annual_production.{pdf,png}\n")
} else {
  cat("WARN: P$AnnualScientProd is NULL\n")
}

# ---- Save: average citations per article per year ----
if (!is.null(P$AverArtCitperYear)) {
  ggsave(file.path(outdir, "fig2_alt_avg_citations_per_article.pdf"),
         plot = P$AverArtCitperYear,
         width = 7, height = 4, device = cairo_pdf)
  ggsave(file.path(outdir, "fig2_alt_avg_citations_per_article.png"),
         plot = P$AverArtCitperYear,
         width = 7, height = 4, dpi = 300, bg = "white")
  cat("Saved: fig2_alt_avg_citations_per_article.{pdf,png}\n")
}

# ---- Top tables for paper supplementary (CSV) ----
safe_csv <- function(obj, name, top_k = 20) {
  if (is.null(obj)) {
    cat(sprintf("  SKIP %s (NULL)\n", name)); return(invisible(NULL))
  }
  df <- as.data.frame(obj)
  if (nrow(df) > top_k) df <- df[seq_len(top_k), , drop = FALSE]
  write.csv(df, file.path(outdir, name), row.names = FALSE)
  cat(sprintf("  wrote %s (%d rows, %d cols)\n",
              name, nrow(df), ncol(df)))
}

cat("=== Top tables ===\n")
safe_csv(results$Sources,
         "table_bibliometrix_top_sources.csv")
safe_csv(results$Authors,
         "table_bibliometrix_top_authors.csv")
safe_csv(results$Countries,
         "table_bibliometrix_top_countries.csv")
safe_csv(results$MostCitedPapers,
         "table_bibliometrix_top_cited_papers.csv")

# ---- Inventory ----
cat("\n=== Files in", outdir, "===\n")
finfo <- file.info(list.files(outdir, full.names = TRUE))
finfo$name <- basename(rownames(finfo))
print(finfo[order(-finfo$mtime), c("name", "size", "mtime")],
      row.names = FALSE)

cat("\n=== Block 2 done ===\n")