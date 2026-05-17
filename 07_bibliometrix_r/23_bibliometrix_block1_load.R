# ============================================================
# Day 12 B — Block 1: bibliometrix load + sanity check
# ============================================================
# Input:  data/raw/wos/*.txt (7 batches, ~3,091 WoS-only records)
# Output: console summary + saved M.rds for next blocks
# Goal:   verify convert2df works; inspect M dimensions and
#         column composition; baseline N for convention check
# ============================================================

suppressPackageStartupMessages(library(bibliometrix))
cat("bibliometrix version:",
    as.character(packageVersion("bibliometrix")), "\n\n")

repo <- "D:/Document/Research-Projects/TCM-HDI-Bibliometric-2026"
setwd(repo)

# Discover 7 WoS batches (exclude wos_partial2026)
wos_files <- list.files("data/raw/wos", pattern = "\\.txt$",
                        full.names = TRUE)
cat("Found", length(wos_files), "WoS .txt files:\n")
for (f in wos_files) cat("  ", basename(f), "\n")
cat("\n")

# Convert to bibliometrix DF (the long-running step; 30-90s typical)
cat("Converting WoS plaintext to bibliometrix DF...\n")
t0 <- Sys.time()
M <- convert2df(file = wos_files,
                dbsource = "wos",
                format   = "plaintext")
cat("convert2df elapsed:",
    round(as.numeric(difftime(Sys.time(), t0, units = "secs")), 1),
    "sec\n\n")

# Sanity dimensions
cat("=== M dimensions ===\n")
cat("rows (records):", nrow(M), "\n")
cat("cols (fields) :", ncol(M), "\n\n")

cat("=== Core bibliometrix columns presence ===\n")
core_cols <- c("AU", "TI", "SO", "PY", "DT", "DE", "ID",
               "AB", "C1", "TC", "DI")
for (cc in core_cols) {
  present <- cc %in% names(M)
  filled  <- if (present)
    sum(!is.na(M[[cc]]) & nchar(as.character(M[[cc]])) > 0) else 0
  cat(sprintf("  %-4s : %s  (%d non-empty)\n",
              cc, ifelse(present, "OK     ", "MISSING"), filled))
}
cat("\n")

cat("=== Document type breakdown ===\n")
print(sort(table(M$DT), decreasing = TRUE))
cat("\n")

cat("=== Publication year range ===\n")
cat("min:", min(M$PY, na.rm = TRUE),
    "  max:", max(M$PY, na.rm = TRUE), "\n")
cat("most recent 10 years:\n")
print(tail(sort(unique(M$PY)), 10))
cat("\n")

# Save M for downstream blocks (skip re-running convert2df)
saveRDS(M, file = "results/figures_bibliometrix/M.rds")
cat("Saved M to results/figures_bibliometrix/M.rds (",
    round(file.size(
      "results/figures_bibliometrix/M.rds") / 1024 / 1024, 1),
    "MB )\n")

cat("\n=== Block 1 done ===\n")