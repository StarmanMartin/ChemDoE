# Define required packages
required_packages <- c("jsonlite", "gtools")

# Install any missing packages
for (pkg in required_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cran.rstudio.com/")
  }
}

# Load the packages
library(jsonlite)
library(gtools)

# Get command-line arguments
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  stop("Usage: Rscript script.R input.json output.json")
}

input_file <- args[1]
output_file <- args[2]

# Read the input JSON file
cat(sprintf("Reading %s\n", input_file))
values <- fromJSON(input_file)

# Define the number of variations to generate
NUMBER_OF_VARIATIONS <- 2

# Calculate context-related values
cat("Calculating context\n")
row_count <- length(values)  # Number of keys (variables)
number_of_options <- length(values[[1]]) - 1  # Options per variable (excluding unit)

arr <- seq(NUMBER_OF_VARIATIONS*number_of_options)

# Generate all permutations
perm <- permutations(length(arr), length(arr), arr, repeats.allowed = FALSE)
perm <- (perm %% 3) + 2
perm <- unique(perm)

perm_idx_lst <- sample(length(perm[,1]))

# Initialize results list with VARIABLE and UNIT vectors
results <- list(VARIABLE = names(values), UNIT = sapply(values, function(x) x[[1]]))


# Generate variations
cat("Preparing Variations\n")
for (i in seq_along(arr)) {
  variation_name <- sprintf("Variation.%d", i - 1)
  results[[variation_name]] <- vector("list", row_count)
  for (r_i in seq_along(values)) {
    perm_idx <- perm[perm_idx_lst[r_i],i]
    r_v <- values[[r_i]]
    results[[variation_name]][[r_i]] <- r_v[perm_idx]
  }
}

# Write the results to the output JSON file
cat(sprintf("Writing %s\n", output_file))
write_json(results, output_file, pretty = TRUE, auto_unbox = TRUE)
