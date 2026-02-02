library(tidyverse)

# --- HUMAN DATA ---
human <- read_csv("/Users/maass/Library/CloudStorage/OneDrive-Personal/Desktop/MPI/TASKS/possibility-generation/LLM_options/Study 3/data/Human_responses_corrected.csv")

human_wide <- human %>%
  group_by(scenario, response_number) %>%
  mutate(block = row_number()) %>%
  ungroup() %>%
  pivot_wider(
    id_cols = block,
    names_from = c(scenario, response_number),
    names_glue = "{scenario}__response_{response_number}",
    values_from = cleaned_response
  )

# extract one response_id per (scenario, block)
human_ids <- human %>%
  group_by(scenario, response_number) %>%
  mutate(block = row_number()) %>%
  ungroup() %>%
  group_by(scenario, block) %>%
  summarise(response_id = first(response_id), .groups = "drop") %>%
  pivot_wider(
    id_cols = block,
    names_from = scenario,
    names_glue = "{scenario}__response_id",
    values_from = response_id
  )

# combine
human_wide <- left_join(human_wide, human_ids, by = "block")

write_csv(
  human_wide,
  "/Users/maass/Library/CloudStorage/OneDrive-Personal/Desktop/MPI/TASKS/possibility-generation/LLM_options/Study 3/data/Human_responses_wide.csv"
)


# --- LLM DATA ---
llm <- read_csv("/Users/maass/Library/CloudStorage/OneDrive-Personal/Desktop/MPI/TASKS/possibility-generation/LLM_options/Study 3/data/LLM_responses_3.csv")

llm_wide <- llm %>%
  group_by(scenario, response_number) %>%
  mutate(block = row_number()) %>%
  ungroup() %>%
  pivot_wider(
    id_cols = block,
    names_from = c(scenario, response_number),
    names_glue = "{scenario}__response_{response_number}",
    values_from = response
  )

llm_ids <- llm %>%
  group_by(scenario, response_number) %>%
  mutate(block = row_number()) %>%
  ungroup() %>%
  group_by(scenario, block) %>%
  summarise(response_id = first(response_id), .groups = "drop") %>%
  pivot_wider(
    id_cols = block,
    names_from = scenario,
    names_glue = "{scenario}__response_id",
    values_from = response_id
  )

llm_wide <- left_join(llm_wide, llm_ids, by = "block")

write_csv(
  llm_wide,
  "/Users/maass/Library/CloudStorage/OneDrive-Personal/Desktop/MPI/TASKS/possibility-generation/LLM_options/Study 3/data/LLM_responses_wide.csv"
)
