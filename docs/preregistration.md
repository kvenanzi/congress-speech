# Pre-registration: party prediction from Congressional floor speech, 104th–119th Congress

Committed 2026-11-05. The git commit that adds this file is the timestamp. It was made before any party classifier was trained, before any party-prediction accuracy was computed, and before any DW-NOMINATE quantity was computed from the downloaded member file. Later changes are listed in the change log at the bottom, each with its reason. None may alter a hypothesis, a test, or a decision rule after the corresponding result has been seen.

**What had been seen before this was written.** These counts come from the feasibility check of 2026-11-05 (`scripts/00_spike.py`):

- **2023, all 213 daily issues:** 99.9% of words in turns that open with a member's name were attributed to a member through the issue's MODS metadata. About four turn openings in the year were missed because of typesetting errors. There were 15,469 member turns of at least 50 words (7,963 Republican, 7,461 Democratic, 39 independent) from 536 speakers. The median length was 241 words.
- **Single issues from 1995, 2001 and 2009:** speaker metadata was present and attributed in the same way.
- **50 random 2023 turns, checked by eye:** all were attributed to the right member with correct boundaries. Two were repeated boilerplate: an arms-export notification read identically by two senators, and a list of absent senators.
- **hein-daily, 114th Congress:** 36,633 member speeches of at least 50 words (19,307 Republican, 17,326 Democratic).
- **2015–2016 GovInfo (114th Congress, 370 issues):** 40,011 member turns of at least 50 words (20,729 Republican, 19,016 Democratic, 206 independent, 60 without a party in MODS) from 544 speakers, with a median of 288 words. In hein-daily, 84.6% of speeches of at least 50 words have a GovInfo turn on the same date whose first 12 words are identical (`scripts/00b_overlap_counts.py`).

No text was classified, no word or phrase frequency was compared between parties, and no DW-NOMINATE statistic was computed. The published result this study extends ([Gentzkow, Shapiro & Taddy 2019](https://doi.org/10.3982/ECTA16566)) and the general rise in roll-call polarization measured by Voteview were known in advance.

## 1. Question

How accurately can a fine-tuned language model identify a member's party from one floor speech, in each Congress from the 104th (1995–1996) to the 119th (2025–2026)? Does that accuracy continue to rise, stay level, or fall after 2016, the last year of the corpus used by Gentzkow, Shapiro & Taddy? Separately, how well does a member's speech predict their DW-NOMINATE first-dimension score, both across the whole chamber and within each party?

## 2. Data

- **Speeches.** The daily Congressional Record from GovInfo, House and Senate sections, from 1 January 1995 to the last issue published on the date of the full fetch (recorded in `data/raw/crec/fetch_log.jsonl` and in the dataset card). Extensions of Remarks and the Daily Digest are excluded, because they are not spoken on the floor. Text is parsed into turns by `congress_speech/crec.py` at the commit that adds this file.
- **Speaker identity.** The bioguide ID comes from the granule's MODS `congMember` record (role `SPEAKING`). If the printed name has no MODS record, the fallback is a unique match on surname, state (when printed), chamber, and Congress against the Voteview member file. Turns that still match no one are dropped.
- **Party and DW-NOMINATE.** Voteview `HSall_members.csv`, downloaded on 2026-11-05: `party_code` (100 = Democratic, 200 = Republican) and `nominate_dim1`, joined on bioguide ID and Congress. Using one source for party in every Congress avoids differences between GPO's metadata and Voteview's.
- **Overlap corpus.** Stanford hein-daily ([Gentzkow, Shapiro & Taddy 2018](https://data.stanford.edu/congress_text)), 104th–114th Congress, used only for H4.

## 3. Units and inclusion

- **Unit:** a turn, meaning one member's contiguous speech, without inserted material (text indented as quotation in the Record).
- **Included turns:** a turn is included if it has at least 50 words and the speaker has party code 100 or 200 in that Congress. The following are excluded:
  - members who changed party within the Congress, for that Congress;
  - independents, for party classification only (they are kept in the H5 regression);
  - delegates and resident commissioners, who are kept, because they speak on the floor under the same rules.
- **Template filter:** within each Congress, a turn is dropped when its first 40 words recur in at least three turns. The first 40 words are compared in lowercase, with digits and punctuation removed. This removes read-in notices and lists of absent members, which are formulaic rather than speech.
- **Congress of a turn:** from the issue date. Congress *k* runs from 3 January of year 1789 + 2(*k* − 1) to 2 January two years later.

## 4. Samples and splits (fixed before any model is trained)

For each Congress, speakers are assigned to train, validation, and test in the ratio 65 / 15 / 20. The assignment is stratified by party and chamber, with seed 20261105, so that no speaker appears in more than one split of a Congress. The test share is larger than the validation share because the Senate supplies only about ten speakers per party to the test split.

Within each split, turns are sampled to fixed counts per party, with the same chamber mix in every Congress: 75% House and 25% Senate. A speaker contributes at most 100 turns to a split, chosen at random. The per-party counts are train 7,000, validation 1,000, and test 2,000. If any Congress cannot supply them after the cap, `scripts/04_build_samples.py` reduces all Congresses to the largest multiple of 500 that every Congress can supply. This rule is mechanical, and it is applied before training. Fixing the counts means that corpus size, party balance, and chamber mix cannot produce a trend in accuracy.

## 5. Models

- **B (baseline).** TF-IDF on word unigrams and bigrams (minimum document frequency 5, sublinear term frequency) with L2 logistic regression. The regularisation strength is chosen on validation accuracy over {0.1, 0.3, 1, 3, 10}, separately per Congress. CPU.
- **T (transformer).** `answerdotai/ModernBERT-base` fine-tuned for binary sequence classification.
  - **Settings.** One set, chosen by an Optuna TPE search of 15 trials on the 108th Congress, maximising validation accuracy. The search covers:
    - learning rate in [1e-5, 1e-4], log scale;
    - epochs in {1, 2, 3};
    - warmup ratio in [0, 0.1];
    - maximum length in {256, 512} tokens;
    - batch size in {16, 32};
    - weight decay in [0, 0.1].
  - **Training.** The chosen settings are then used without change for every Congress, with seed 20261105.
  - **Extra seeds.** The 115th and 119th Congresses are also trained with seeds 1 and 2, to estimate seed variation. Their reported accuracy is the mean of the three seeds.
- **Accuracy.** Measured on the test split of each Congress. The 95% interval is a cluster bootstrap over test speakers: speakers are resampled with replacement, with all of their test turns, 2,000 resamples, seed 20261105.

## 6. Hypotheses and decision rules

- **H1 (validity).** Accuracy of T across the 16 Congresses rises and falls with the gap between the parties' mean DW-NOMINATE first dimension. The gap is the Republican mean minus the Democratic mean, over members of both chambers with at least one included turn.
  - **Test:** Spearman ρ between the two series.
  - **Supported** if ρ > 0.7. The bootstrap interval of ρ is reported, from resampling Congresses.
- **H2 (headline).** The trend in T's accuracy over the 115th–119th Congresses (2017–2026).
  - **Test:** the OLS slope of accuracy on Congress number, with a 95% interval from 2,000 joint cluster-bootstrap replicates of the five accuracies.
  - **Rising** if the interval is above zero, **falling** if it is below zero, and **not distinguishable** otherwise.
  - The same slope over the 104th–114th Congresses is reported for comparison but is not tested.
- **H3 (model).** T is more accurate than B.
  - **Supported** if T's accuracy is higher in all 16 Congresses and the 95% bootstrap interval of the mean paired difference excludes zero.
- **H4 (source).** The change of source at 2017 does not create the trend. For each of the 104th–114th Congresses, B is trained and tested on hein-daily turns with the same inclusion, template, sample, and split rules, and compared with B on GovInfo turns.
  - **Supported** if the GovInfo and hein-daily accuracies lie within each other's 95% intervals in at least 9 of the 11 Congresses, and Spearman ρ between the two series exceeds 0.8.
- **H5 (speech and votes).** The unit is a member in a Congress with at least 10 included turns, independents included.
  - **Features:** the mean over the member's turns of `BAAI/bge-base-en-v1.5` sentence embeddings, truncated at 512 tokens.
  - **Model:** ridge regression on `nominate_dim1`, with α chosen by inner cross-validation over {0.1, 1, 10, 100}.
  - **Folds:** five-fold GroupKFold grouped by bioguide ID across all Congresses, so that no member appears in both the training and test folds.
  - **Prediction:** held-out Pearson r over all members is above 0.85, and within each party, the held-out r is below 0.5 for Democrats and below 0.5 for Republicans. Each of the three parts gets its own verdict. Intervals are bootstrapped over members.
  - **Reporting:** the ten largest absolute residuals within each party are listed with the member's name, Congress, and score, without characterisation.

## 7. Sensitivity analyses (reported, not decisive)

- **S1.** T's test accuracy after masking these words in test text only: Democrat, Democrats, Democratic, Republican, Republicans, and GOP, each replaced with `[PARTY]`.
- **S2.** Accuracy by chamber.
- **S3.** Accuracy by length tercile.
- **S4.** Recall for each party separately, and whether the majority party in a chamber is identified more accurately than the minority party.
- **S5.** B fitted with the same samples, for every hypothesis that uses T.

## 8. Tracking and publication

All runs are logged to the MLflow experiment `congress-speech` (`mlflow.withinnoise.dev`), and per-turn test predictions are stored as artifacts. The parsed speech table goes to the Hugging Face dataset `kvenanzi/congressional-record-speeches-1995-2026`, and the T model for the 119th Congress goes to `kvenanzi/congress-party-classifier`. Both are created private and made public after review.

## Change log

- **2026-11-05, before any classifier was trained or any accuracy computed (clarification of §3).** Non-voting delegates and the resident commissioner (DC, Puerto Rico, Guam, the Virgin Islands, American Samoa, the Northern Mariana Islands) are excluded from every Congress. §3 kept them, but the Voteview file lists them only in Congresses in which they could vote in the Committee of the Whole (for example not in the 114th), so under the party rule of §2 they would have been included in some Congresses and not others. Excluding them everywhere keeps the set of eligible speakers the same in kind across Congresses. In the 114th Congress this affects 291 of 40,019 turns of 50 or more words.
- **2026-11-05, after the sweep and before any per-Congress run of T (record of a tie).** Four of the 15 trials (3, 4, 9 and 11) reached the same validation accuracy, 0.7465 (1,493 of 2,000 turns). §5 does not say how a tie is broken. The settings used are those of trial 3, the first of the four, which is what Optuna's `best_trial` returns. Trial 3 is also among the cheapest of the four (2 epochs, against 3 for trials 4 and 9). No test-split accuracy had been computed for any trial.
