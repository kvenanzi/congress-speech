# Citation check record

Not published (md2qmd ignores this file). Checked 2026-11-06 in three passes:

1. **Finding pass:** sources located by search, metadata confirmed against Crossref or the provider page, and quotes collected (section 1 below).
2. **Checking pass A:** gentzkow2019, gentzkow2018, peterson2018, lewis2026, voteview2026a/b, diermeier2012, and the AP link (section 2).
3. **Checking pass B:** lauderdale2016, warner2025, xiao2024, nosek2018, akiba2019, hoerl1970 (section 3).

## Changes made to the post after the checks

- **Gentzkow et al 2019:** "fairly stable for a century, then rose from the early 1990s" replaced with the paper's own figures (54% in 1873, 57% in 1990, 73% in 2007–2009) and its dating of the rise to the 1994 election.
- **Lauderdale & Herzog 2016:** the draft said speech agrees with votes across parties but much less within them. The paper reports a single moderate within-party correlation (ρ = 0.46, both parties pooled, senators 1995–2014, its own IRT vote scale), so both citing sentences were narrowed to that, and the comparison with this project's results is marked as not directly comparable.
- **Voteview:** the data page supports only the "economic liberalism–conservatism" reading of the first dimension. The About page was added (voteview2026a) for how the map is built, and the claim about the growing party gap now points to this project's own Figure 1 rather than to a citation.
- **Peterson & Spirling 2018:** "British Parliament" narrowed to "British House of Commons".
- **hein-daily:** described as the Gentzkow, Shapiro, and Taddy parse distributed by Stanford, covering the 97th–114th Congresses, of which the 104th–114th were used.
- **Boche et al 2018:** dropped (abstract only, and not needed once the Voteview pages were cited).
- **Nosek et al 2018, Warner et al 2025:** small wording changes.
- **Abstract only:** Diermeier et al 2012 (paywalled). The post cites it only for "classified senators by ideology from their speeches", which the abstract supports.

---

# 1. Finding pass

# Sources found for the post

Checked 2026-11-06. Metadata for every bib entry comes from the Crossref API
(`https://api.crossref.org/works/<doi>`) or from the publisher / data-provider page, as noted
for each source. Quotes are copied verbatim from the text I read. I have not corrected them;
line-break hyphens from PDF extraction are removed. Where the PDF text had lost its word
spaces, I say so. Square brackets with an ellipsis, "[...]", mark text I cut.

Keys in `references.bib`: gentzkow2019, gentzkow2018, peterson2018, lewis2026, voteview2026,
boche2018, warner2025, xiao2024, diermeier2012, lauderdale2016, nosek2018, akiba2019,
hoerl1970.

---

## 1. gentzkow2019: Gentzkow, Shapiro & Taddy (2019), Econometrica 87(4):1307–1340

- Crossref: https://api.crossref.org/works/10.3982/ecta16566 (authors, title, volume 87, issue 4, pages 1307–1340, year 2019 all match what you listed)
- Full text read: the published Econometrica version hosted by the author, https://web.stanford.edu/~gentzkow/research/politext.pdf (header reads "Econometrica, Vol. 87, No. 4 (July, 2019), 1307–1340").
- Also read: NBER Working Paper 22423, revised March 2019, https://www.nber.org/system/files/working_papers/w22423/w22423.pdf. The quotes below come from the published version. The NBER text gives the same numbers.
- **Full text read.**

**Partisanship is defined as how easily an observer could guess party (abstract, p. 1307):**

> "We apply this method to measure trends in the partisanship of congressional speech from 1873 to 2016, defining partisanship to be the ease with which an observer could infer a congressperson's party from a single utterance. Our estimates imply that partisanship is far greater in recent years than in the past, and that it increased sharply in the early 1990s after remaining low and relatively constant over the preceding century."

> "We measure partisan differences in speech in a given session of Congress by the ease with which an observer who knows the model could guess a speaker's party based solely on the speaker's choice of a single phrase. We call this measure partisanship for short." (Introduction, p. 1308)

**Data run through the 114th Congress / 2016:**

> "Our primary data source is the text of the United States Congressional Record (hereafter, the Record) from the 43rd Congress to the 114th Congress." (Section 2, pp. 1310–1311)

> "Our data contain bound editions for the 43rd to 111th Congresses, and daily editions for the 97th to 114th Congresses. We use the bound edition in the sessions where it is available and the daily edition thereafter." (p. 1311)

**Stable for a long period, then a sharp rise from the early-to-mid 1990s, with the one-minute-speech numbers:**

> "We find that the partisanship of language has exploded in recent decades, reaching an unprecedented level. From 1873 to the early 1990s, partisanship was nearly constant and fairly small in magnitude: in the 43rd session of Congress (1873–1875), the probability of correctly guessing a speaker's party based on a one-minute speech was 54 percent; by the 101st session (1989–1990), this figure had increased to 57 percent. Beginning with the congressional election of 1994, partisanship turned sharply upward, with the probability of guessing correctly based on a one-minute speech climbing to 73 percent by the 110th session (2007–2009)." (pp. 1308–1309)

> "Looking at the data through the sharper lens of the leave-out and penalized estimators reveals that partisanship was low and relatively constant until the early 1990s, then exploded, reaching unprecedented heights in recent years." (Section 5, p. 1320)

> "An average one-minute speech in our data contains around 33 phrases (after pre-processing). In 1874, an observer hearing such a speech would expect to have a posterior of around 0.54 on the speaker's true party, only slightly above the prior of 0.5. By 1990, this value increased slightly to 0.57. Between 1990 and 2008, however, it leaped up to 0.73." (pp. 1320–1322)

Notes for the post:
- The last Congress with a one-minute-speech figure is the **110th (2007–2009): 73 percent**. The text gives no one-minute number for the 111th–114th Congresses. Figure 3 plots only 1873–1874, 1989–1990 and 2007–2008. Don't attribute a 114th-Congress percentage to them.
- The paper says "session" where it means a whole Congress (e.g. "the 110th session (2007–2009)").
- The figures are the expected posterior an observer would assign to the true party, and the paper calls this the "probability of correctly guessing". They are not a classifier's held-out accuracy.
- Possibly useful: "Across all sessions, the correlation between speech and roll-call based partisanship measures is 0.537 (p = 0.000). After controlling for party, the correlation is 0.129" (NBER w22423 p. 22. I did not re-check this sentence in the published version).

---

## 2. gentzkow2018: Stanford "hein-daily" dataset

- Page read: https://data.stanford.edu/congress_text (Stanford Libraries Social Science Data Collection). **Read the dataset landing page in full. I did not open the codebook PDF.**
- Discrepancy: I found **no PURL or DOI**. DataCite returned 0 matches and the landing page gives only the URL, so the bib entry uses the URL. (An older, different ICPSR release, "Congressional Record for 104th–110th Congresses: Text and Phrase Counts", ICPSR 33501, does have a DOI. It is not this dataset.)
- Licence: confirmed as **ODC-By v1.0**.

> "How to Cite this Dataset: Gentzkow, Matthew, Jesse M. Shapiro, and Matt Taddy. Congressional Record for the 43rd-114th Congresses: Parsed Speeches and Phrase Counts. Palo Alto, CA: Stanford Libraries [distributor], 2018-01-16. https://data.stanford.edu/congress_text"

> "This dataset contains processed text from the bound and daily editions of the United States Congressional Record, as provided by HeinOnline. The bound edition covers the 43rd to 111th Congresses, and the daily edition covers the 97th to 114th."

> "Time span: 1873–2017 (43rd–114th US Congress) Time of data collection: 1873–2011 (bound), 1981–2017 (daily)"

> "Open Data Commons Attribution License (ODC-By) v1.0"

> "Attribute: You must attribute any public use of the data, or works produced from the data, in the manner specified in the license. For any use or redistribution of the data, or works produced from it, you must make clear to others the license of the data and keep intact any notices on the original data."

The download list includes "hein-daily.zip".

Note: the page gives the time span as 1873–2017, because the 114th Congress ended on 3 January 2017. The paper's abstract says "1873 to 2016".

---

## 3. peterson2018: Peterson & Spirling (2018), Political Analysis 26(1):120–128

- Crossref: https://api.crossref.org/works/10.1017/pan.2017.39 (matches what you listed)
- Full text PDF from Cambridge: https://www.cambridge.org/core/services/aop-cambridge-core/content/view/45746D999CFCD1CB43E362392D7B2FB4/S1047198717000390a.pdf/classification-accuracy-as-a-substantive-quantity-of-interest-measuring-polarization-in-westminster-systems.pdf
- **Full text read.** The abstract quotes below come from the Crossref abstract field, which has proper spacing. The PDF's text layer has most word spaces missing, so for the body quote I restored the spaces. Each word and punctuation mark is as printed.

> "We suggest a new measurement strategy that makes innovative use of the "accuracy" of machine classifiers, i.e., the number of correct predictions made as a proportion of all predictions. In our case, the "labels" are the party identifications of the members of parliament, predicted from their speeches along with some information on debate subjects. Intuitively, when the learner is able to discriminate members in the two main Westminster parties well, we claim we are in a period of "high" polarization. By contrast, when the classifier has low accuracy—and makes a relatively large number of mistakes in terms of allocating members to parties based on the data—we argue parliament is in an era of "low" polarization." (abstract)

> "More broadly, we show that the technical performance of supervised learning algorithms can be directly informative about substantive matters in social science." (abstract)

> "When the machine learning accuracy—in the technical sense—is low, Labour MPs cannot easily be told apart from Conservative MPs (at least in terms of their speech contents). We deduce then that we are in a world of relatively low polarization." (p. 121; spaces restored)

Note: their application is the UK House of Commons (78 years of speeches), not the US Congress. The paper also cites Gentzkow, Shapiro, and Taddy (2016), the working-paper version, as "similar in spirit".

---

## 4. Voteview: lewis2026 (database), voteview2026 (field description), boche2018 (journal article)

### lewis2026: the database's requested citation

- Page read: https://voteview.com/data. **Read in full.**
- Discrepancy: the year in the requested citation is generated from the current date, and today it reads **2026**. The author list matches what you gave. Poole is given as "Keith Poole", with no middle initial.

> "Please cite the dataset as: Lewis, Jeffrey B., Keith Poole, Howard Rosenthal, Adam Boche, Aaron Rudkin, and Luke Sonnet (2026). Voteview: Congressional Roll-Call Votes Database. https://voteview.com/"

### voteview2026: what the first dimension is (**this is the source whose text actually says it**)

- Page read: https://voteview.com/articles/data_help_members ("Data - Member Ideology", byline "Voteview", dated January 22, 2026). This is the documentation for HSall_members.csv. **Read in full.**

> "Quick Link (all congresses, all chambers, CSV format): https://voteview.com/static/data/out/members/HSall_members.csv"

> "nominate_dim1 : NOMINATE first dimension estimate."

> "We expect that most users of our data will primarily make use of the nominate_dim1 field, which reports the first dimension (often interpreted as economic liberalism-conservatism) of members as estimated by NOMINATE. For more information on these scores, please see discussion in our journal article: Boche, Adam, Jeffrey B. Lewis, Aaron Rudkin, and Luke Sonnet. "The new Voteview.com: preserving and continuing Keith Poole's infrastructure for scholars, students and observers of Congress". Public Choice 176(1-2)."

Supporting text from the undated About page, https://voteview.com/about (read in full, not in the bib):

> "Ideological positions are calculated using the DW-NOMINATE (Dynamic Weighted NOMINAl Three-step Estimation). This procedure was developed by Poole and Rosenthal in the 1980s and is a "scaling procedure", representing legislators on a spatial map. In this sense, a spatial map is much like a road map--the closeness of two legislators on the map shows how similar their voting records are. Using this measure of distance, DW-NOMINATE is able to recover the "dimensions" that inform congressional voting behavior. The primary dimension through most of American history has been "liberal" vs. "conservative" (also referred to as "left" vs. "right")."

### boche2018: Boche, Lewis, Rudkin & Sonnet (2018), Public Choice 176(1–2):17–32

- Crossref: https://api.crossref.org/works/10.1007/s11127-018-0546-0 (authors, title, volume, issue and pages confirmed. Online 2018-05-07, print issue July 2018)
- Abstract read on IDEAS/RePEc: https://ideas.repec.org/a/kap/pubcho/v176y2018i1d10.1007_s11127-018-0546-0.html
- **Abstract only.** The article is closed access (OpenAlex: "closed"), and link.springer.com blocked automated access.

> "At Poole's Voteview.com, scholars, students, journalists, and the broader public could download gold-standard historical and current roll-call voting data, member rosters, NOMINATE scores, and measures and visualizations of party cohesion and polarization, among many other useful things. In this article, we describe how we are preserving and continuing these vast public-goods contributions through the new Voteview.com."

**Which one to cite for "first dimension is read as liberal–conservative":** use **voteview2026** (and the About page). In what I could read of Boche et al., which is only the abstract, the first dimension is never described as liberal–conservative. I could not read the full text, so I can't confirm whether the body does. I did not find an open copy of Poole & Rosenthal's peer-reviewed DW-NOMINATE papers either: Poole & Rosenthal (2001), "D-Nominate after 10 Years", *Legislative Studies Quarterly* 26(1):5–, doi:10.2307/440401, and the 1985 AJPS NOMINATE paper. So neither is in the bib. One more option: a 2008 preliminary draft of Carroll, Lewis, Lo, Poole & Rosenthal, "Measuring Bias and Uncertainty in DW-NOMINATE Ideal Point Estimates via the Parametric Bootstrap" (https://legacy.voteview.com/pdf/nomboot.pdf), says "Previous research has demonstrated that the first dimension locations reveal standard left-right or economic cleavages, while the second dimension locations reflect social and sectional divisions." That draft is marked "Preliminary Draft, please do not cite without permission", and I did not confirm the published version, so I left it out.

Wording to keep: Voteview says "often interpreted as **economic** liberalism-conservatism", and that the liberal–conservative split has held "through most of American history". Both are softer than "is" liberal–conservative.

---

## 5. warner2025: ModernBERT, ACL 2025 (Volume 1: Long Papers), pp. 2526–2547

- Published version exists: ACL 2025, so I used that rather than arXiv.
- Crossref: https://api.crossref.org/works/10.18653/v1/2025.acl-long.127
- ACL Anthology BibTeX: https://aclanthology.org/2025.acl-long.127.bib (editors, Vienna, pages 2526–2547)
- Full text read: https://aclanthology.org/2025.acl-long.127.pdf. arXiv abstract page checked: https://arxiv.org/abs/2412.13663
- **Full text read.**
- **Discrepancy in the author list.** The paper PDF and arXiv list **14** authors, including **Nathan Cooper** (between Aarsen and Adams). Crossref and the ACL Anthology metadata list 13 and leave him out. The PDF also gives "Griffin Adams", while the Anthology has "Griffin Thomas Adams". The bib follows the paper itself: 14 authors, with "Adams, Griffin".

> "Encoder-only transformer models such as BERT offer a great performance-size tradeoff for retrieval and classification tasks with respect to larger decoder-only models." (abstract)

> "In this paper, we introduce ModernBERT, bringing modern model optimizations to encoder-only models and representing a major Pareto improvement over older encoders. Trained on 2 trillion tokens with a native 8192 sequence length, ModernBERT models exhibit state-of-the-art results on a large pool of evaluations encompassing diverse classification tasks and both single and multi-vector retrieval on different domains (including code)." (abstract)

> "Both ModernBERT models are trained on 2 trillion tokens of primarily English data from a variety of data sources, including web documents, code, and scientific literature, following common modern data mixtures." (Section 2.2.1)

> "ModernBERT has a native sequence length of 8,192 tokens and incorporates recent architecture improvements, such as GeGLU layers, RoPE positional embeddings, and alternating local-global attention." (Conclusion)

Note: the appendix training table splits the 2T as "1.719 trillion" + "250 billion" + "50 billion" tokens across phases, with a max sequence length of 1,024 in the first phase and 8,192 in the later ones.

---

## 6. xiao2024: C-Pack, SIGIR 2024, pp. 641–649

- Crossref: https://api.crossref.org/works/10.1145/3626772.3657878 (6 authors, pages 641–649)
- Full text read: arXiv 2309.07597, latest version PDF https://arxiv.org/pdf/2309.07597. It carries the SIGIR '24 header and "ACM Reference Format", so it is the camera-ready text. Abs page: https://arxiv.org/abs/2309.07597v4
- Model card read: https://huggingface.co/BAAI/bge-base-en-v1.5 (README)
- **Full text read.**
- **Discrepancies:**
  - The SIGIR title is **"C-Pack: Packed Resources For General Chinese Embeddings"**. You had "Packed resources for general Chinese embeddings", which matches. The arXiv listing metadata and the model card's citation still use the earlier title, "C-Pack: Packaged Resources To Advance General Chinese Embedding".
  - The SIGIR version has **6 authors**: Xiao, Liu, Zhang, Muennighoff, Lian, Nie. The model card's citation lists only the first 4.
  - The paper **does** discuss the English models and reports small, base and large English results on MTEB in Table 5. It **does not mention v1.5**. "bge-base-en-v1.5" and the v1.5 release appear only on the Hugging Face model card / FlagEmbedding README, and that card cites this paper.

> "3) BGE is a family of embedding models covering multiple sizes. [...] Along with our resources on general Chinese embedding, we release our data and models for English text embeddings. The English models also achieve state-of-the-art performance on the MTEB benchmark; meanwhile, our released English data is 2 times larger than the Chinese data." (abstract)

> "Using the same recipe as the Chinese models, we also train a set of English text embedding models presented in Table 5." (Section 4.1)

> "BGE (BAAI General Embeddings). We provide a family of well-trained models for Chinese general text embeddings. There are three optional model sizes: small (24M), base (102M), and large (326M)" (Section 1)

From the model card (https://huggingface.co/BAAI/bge-base-en-v1.5):

> "09/12/2023: New models: [...] **update embedding model**: release `bge-*-v1.5` embedding model to alleviate the issue of the similarity distribution, and enhance its retrieval ability without instruction."

---

## 7. diermeier2012: Diermeier, Godbout, Yu & Kaufmann (2012), BJPolS 42(1):31–55

- Crossref: https://api.crossref.org/works/10.1017/s0007123411000160 (online 2011-05-23, print issue January 2012). The Cambridge page shows the issue date as "01 December 2011". 2012 is the issue year Crossref records and the year you gave.
- Cambridge article page: https://www.cambridge.org/core/journals/british-journal-of-political-science/article/language-and-ideology-in-congress/1063F5509BC2ABC3F9A0E164E58157EE. The page shows the abstract and, with the references, the article's footnotes.
- **Abstract and footnotes only.** The body is paywalled and I found no open copy.

> "Legislative speech records from the 101st to 108th Congresses of the US Senate are analysed to study political ideologies. A widely-used text classification algorithm – Support Vector Machines (SVM) – allows the extraction of terms that are most indicative of conservative and liberal positions in legislative speeches and the prediction of senators' ideological positions, with a 92 per cent level of accuracy. Feature analysis identifies the terms associated with conservative and liberal ideologies. The results demonstrate that cultural references appear more important than economic references in distinguishing conservative from liberal congressional speeches, calling into question the common economic interpretation of ideological differences in the US Congress." (abstract)

> "We used the Poole and Rosenthal dw-nominate scores available at http://voteview.com/dwnomin.htm ." (footnote 17)

> "The dw-nominate scores for the same senators can be different across congresses. As a result, when we prepare the senatorial speeches as training and testing documents (each document is called an 'example' in machine learning terms), a senator could be assigned to the extreme category in one congress but moved to the moderate category in another." (footnote 19)

> "Forty-five of these fifty 'extreme' senators had already served in the 107th Congress." (footnote 20)

Note: the footnotes suggest the 92 percent applies to senators sorted into categories by DW-NOMINATE, including a set of fifty "extreme" senators. I could not read the body text that defines the exact classification task, so be careful about how "92 per cent" is described.

---

## 8. lauderdale2016: Lauderdale & Herzog (2016), Political Analysis 24(3):374–394

- Crossref: https://api.crossref.org/works/10.1093/pan/mpw017 (matches what you listed)
- Full text read: the accepted version on LSE Research Online (November 2016 deposit, which gives the 24(3) pp. 374–394 citation), https://researchonline.lse.ac.uk/id/eprint/66498/7/Lauderdale_Measuring%20political.pdf. Its abstract is word-for-word the Crossref abstract.
- **Full text read (accepted manuscript).**
- **Discrepancy with your claim.** The paper does **not** say speech positions agree with roll-call positions across parties but much less within parties. It reports a **moderate within-party correlation of 0.46** between speech and roll-call scores, says the three measures are "positively and similarly correlated within as well as across parties", and finds **more cross-party overlap in speech than in roll calls**. Also, its roll-call scale is the authors' own Bayesian IRT model fitted to the same period, not DW-NOMINATE.

> "In the US Senate, we estimate a dimension that has moderate within-party correlations with scales based on roll-call votes and campaign donation patterns, however we observe greater overlap across parties in speech positions than roll-call positions and partisan polarization in speeches varies more clearly in response to major political events." (abstract)

> "While estimates from all three methods are positively and similarly correlated within as well as across parties, we find a much larger increase in speech polarization compared to (already high) roll-call polarization." (Introduction, pp. 2–3 of manuscript)

> "For roll-call votes, we fit a standard Bayesian IRT model to all votes over the same period as our speeches." (Section 5.1)

> "If we calculate correlations between within-party variation in these three scores, we find that roll-call scores are correlated with speech scores at ρ = 0.46, while donor scores are correlated with roll-call scores at ρ = 0.57 and with speech scores at ρ = 0.55." (Section 5.1)

> "A striking difference is that the gap between the average party positions in speeches has doubled, a far larger increase than for roll-call voting. [...] Whereas Republican and Democratic senators used to substantially overlap in how they spoke on the floor, that overlap has mostly disappeared over the last two decades due to turnover." (Section 5.2, covering 1995 to 2014)

---

## 9. nosek2018: Nosek, Ebersole, DeHaven & Mellor (2018), PNAS 115(11):2600–2606

- Crossref: https://api.crossref.org/works/10.1073/pnas.1708274114 (matches what you listed)
- Full text read: PubMed Central, https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/ (pnas.org blocked automated access)
- **Full text read.**

> "This distinction between postdiction and prediction is appreciated conceptually but is not respected in practice. Mistaking generation of postdictions with testing of predictions reduces the credibility of research findings." (abstract)

> "An effective solution is to define the research questions and analysis plan before observing the research outcomes—a process called preregistration. Preregistration distinguishes analyses and outcomes that result from predictions from those that result from postdictions." (abstract)

> "In postdiction, the data are already known and the postdiction is generated to explain why they occurred."

> "Preregistration is a solution that helps researchers maintain clarity between prediction and postdiction and preserve accurate calibration of evidence."

> "Preregistration in Practice Preregistration does not favor prediction over postdiction; its purpose is to make clear which is which." (the first two words are the section heading)

> "In principle, preregistration can establish a bright line between prediction and postdiction."

---

## 10. akiba2019: Akiba, Sano, Yanase, Ohta & Koyama (2019), KDD '19, pp. 2623–2631

- Crossref: https://api.crossref.org/works/10.1145/3292500.3330701. Crossref splits the title into "Optuna" plus the subtitle "A Next-generation Hyperparameter Optimization Framework". Pages 2623–2631, ACM, New York, NY, USA.
- Full text read: arXiv preprint 1907.10902, https://arxiv.org/pdf/1907.10902 ("Preprint, compiled July 26, 2019"). Its abstract is identical to the KDD abstract in OpenAlex.
- Optuna docs read: https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html and https://optuna.readthedocs.io/en/stable/reference/generated/optuna.create_study.html
- **Full text read (arXiv preprint). I did not read the ACM version of the body.**

> "The criteria we propose include (1) define-by-run API that allows users to construct the parameter search space dynamically, (2) efficient implementation of both searching and pruning strategies, and (3) easy-to-setup, versatile architecture that can be deployed for various purposes" (abstract)

> "Our Optuna features both, and it can handle various independent sampling methods including TPE as well as relational sampling methods like CMA-ES." (Section 3.1)

The paper cites TPE to Bergstra et al. (its ref. [6]) and calls it "tree-structured Parzen estimator (TPE)". That TPE is Optuna's **default** sampler comes from the current docs, not the paper:

> "Sampler using TPE (Tree-structured Parzen Estimator) algorithm. On each trial, for each parameter, TPE fits one Gaussian Mixture Model (GMM) l(x) to the set of parameter values associated with the best objective values, and another GMM g(x) to the remaining parameter values. It chooses the parameter value x that maximizes the ratio l(x)/g(x)." (TPESampler docs)

> "If None is specified, TPESampler is used as the default." (create_study docs, `sampler` argument)

---

## 11. hoerl1970: Hoerl & Kennard (1970), Technometrics 12(1):55–67

- Crossref: https://api.crossref.org/works/10.1080/00401706.1970.10488634 (authors, title, 12(1), pp. 55–67, February 1970). Crossref also has a 2000 reprint in Technometrics 42(1):80–86, doi:10.1080/00401706.2000.10485983. Cite the 1970 original.
- Abstract read via OpenAlex (https://api.openalex.org/works/doi:10.1080/00401706.1970.10488634). tandfonline.com returned 403, so I could not see the abstract on the publisher page.
- **Abstract only (from OpenAlex, not the publisher page).**

> "In multiple regression it is shown that parameter estimates based on minimum residual sum of squares have a high probability of being unsatisfactory, if not incorrect, if the prediction vectors are not orthogonal. Proposed is an estimation procedure based on adding small positive quantities to the diagonal of X′X. Introduced is the ridge trace, a method for showing in two dimensions the effects of nonorthogonality. It is then shown how to augment X′X to obtain biased estimates with smaller mean square error."

---

## 12. News: Democrats win the House and Senate (midterms of Tuesday 3 November 2026). Inline link, not in bib

apnews.com itself is not reachable from my tools. I could not open the story on AP's own site. I found and read the **AP wire story as republished by PBS News**, with AP bylines and an "(AP)" dateline:

- URL: https://www.pbs.org/newshour/politics/democrats-win-control-of-the-u-s-house
- Headline: "Democrats win control of U.S. House, in major rebuke to Trump"
- Byline: Jill Colvin, Mary Clare Jalonick and Will Weissert, Associated Press
- Date: page metadata `datePublished` 2026-11-04T01:27:26-05:00 (4 November 2026)
- **Full text read (first section).**

> "WASHINGTON (AP) — Democrats have won control of the U.S. House in addition to the U.S. Senate, delivering a shockingly decisive rebuke of Republican governance in Washington and ushering in a new era of congressional resistance to President Donald Trump."

> "The midterm elections that came to a close Tuesday channeled voters' deep frustrations over high prices, the Iran war and concerns over government corruption."

Also read: the earlier AP story on the Senate alone (PBS, by "Associated Press", 2026-11-03T23:40:42-05:00), https://www.pbs.org/newshour/politics/democrats-take-control-of-the-senate-after-winning-key-midterm-races. Headline "Democrats take control of the Senate after winning key midterm races":

> "WASHINGTON (AP) — Democrats have retaken control of the U.S. Senate, delivering a decisive rebuke of Republican control of governance in Washington and ushering in a new era of congressional resistance to President Donald Trump."

Caveat: on 4–5 November, other outlets reported that some individual House and Senate races had not yet been called. By then the AP had already called control of both chambers for Democrats.

---

# 2. Checking pass A

# Citation check results, set A

Checked 2026-11-06. Sources: gentzkow2019, gentzkow2018, peterson2018, lewis2026, voteview2026, diermeier2012, AP news link.
Downloaded copies (untrusted data, text only) are in the scratchpad `dl_*` folders; `g19.txt` is the text extracted from the Gentzkow et al 2019 PDF.

---

## gentzkow2019: Gentzkow, Shapiro & Taddy (2019), Econometrica 87(4):1307–1340

**Metadata: OK.** Crossref (https://api.crossref.org/works/10.3982/ECTA16566) gives the title "Measuring Group Differences in High‐Dimensional Choices: Method and Application to Congressional Speech", authors Matthew Gentzkow, Jesse M. Shapiro and Matt Taddy, *Econometrica* 87(4), pages 1307–1340, 2019. The PDF header reads "Econometrica, Vol. 87, No. 4 (July, 2019), 1307–1340". All fields match the reference list and the BibTeX.

**Support**

Paragraph 1: "asked how easily someone could guess a member's party from their speech in Congress, and found that it became much easier starting in the mid-1990s … Their data end in 2016."
- **Verdict: yes.** One wording note follows below.
- p. 1307 (abstract): "We apply this method to measure trends in the partisanship of congressional speech from 1873 to 2016, deﬁning partisanship to be the ease with which an observer could infer a congressperson's party from a single utterance. Our estimates imply that partisanship is far greater in recent years than in the past, and that it increased sharply in the early 1990s after remaining low and relatively constant over the preceding century."
- p. 1309: "Beginning with the congressional election of 1994, partisanship turned sharply upward"
- p. 1332: "The inﬂection point in the partisanship series occurs around the 104th session (1995–1996), the ﬁrst following the 1994 midterm election."
- Note: the abstract says "early 1990s", but the body puts the turn at the 1994 election and the 104th session (1995–96). "Mid-1990s" fits the body. If you want to match the paper's own words exactly, write "starting with the 1994 election".

Paragraph 2: "how well an observer who hears a short piece of speech can guess the speaker's party. By their estimate, the chance of guessing right from a one-minute speech changed little between 1873 (54%) and 1990 (57%), then rose to 73% by 2007–2009, with the rise beginning around the 1994 election."
- **Verdict: yes.** All three numbers, both periods and the 1994 timing check out.
- p. 1308: "We measure partisan differences in speech in a given session of Congress by the ease with which an observer who knows the model could guess a speaker's party based solely on the speaker's choice of a single phrase. We call this measure partisanship for short."
- p. 1309: "From 1873 to the early 1990s, partisanship was nearly constant and fairly small in magnitude: in the 43rd session of Congress (1873–1875), the probability of correctly guessing a speaker's party based on a one-minute speech was 54 percent; by the 101st session (1989–1990), this ﬁgure had increased to 57 percent. Beginning with the congressional election of 1994, partisanship turned sharply upward, with the probability of guessing correctly based on a one-minute speech climbing to 73 percent by the 110th session (2007–2009)."
- p. 1321 (Section 5): "An average one-minute speech in our data contains around 33 phrases (after pre-processing). In 1874, an observer hearing such a speech would expect to have a posterior of around 0.54 on the speaker's true party, only slightly above the prior of 0.5. By 1990, this value increased slightly to 0.57. Between 1990 and 2008, however, it leaped up to 0.73."
- Minor point: strictly, the quantity is the expected posterior on the true party, which the paper's introduction calls "the probability of correctly guessing". The post follows the introduction, so this is fine.

**Evidence level:** full text. I read the published Econometrica PDF on the author's site.
**URLs:** https://api.crossref.org/works/10.3982/ECTA16566 ; https://web.stanford.edu/~gentzkow/research/politext.pdf

---

## gentzkow2018: Gentzkow, Shapiro & Taddy (2018), Congressional Record parsed speeches (Stanford Libraries)

**Metadata: OK.** The dataset page quotes its recommended citation as: "Gentzkow, Matthew, Jesse M. Shapiro, and Matt Taddy. Congressional Record for the 43rd-114th Congresses: Parsed Speeches and Phrase Counts. Palo Alto, CA: Stanford Libraries [distributor], 2018-01-16. https://data.stanford.edu/congress_text". The page also says: "Open Data Commons Attribution License (ODC-By) v1.0". Title, authors, distributor, date and licence all match. (The page's bibliography section spells the third author "Matthew Taddy", but its citation block uses "Matt Taddy", which agrees with your entry.)

**Support**

"Stanford's hein-daily parse of the Record (Gentzkow et al 2018), 104th–114th Congresses, used only for question 4."
- **Verdict: yes.** Two small wording notes follow.
- Abstract on the page: "This dataset contains processed text from the bound and daily editions of the United States Congressional Record, as provided by HeinOnline. The bound edition covers the 43rd to 111th Congresses, and the daily edition covers the 97th to 114th." The download list includes "hein-daily.zip".
- The daily edition covers the 97th–114th Congresses, so 104th–114th is a subset you chose. The wording does not say that, and a reader could take 104th–114th as the full extent of the dataset.
- The parse was made by Gentzkow, Shapiro and Taddy from HeinOnline text, and Stanford Libraries distributes it. "Stanford's" is loose.
- Optional narrower wording: "the hein-daily parse of the Record by Gentzkow et al, distributed by Stanford Libraries ([Gentzkow et al 2018](#references)); I used its 104th–114th Congresses, and only for question 4."

**Evidence level:** the dataset landing page, which is the primary source for these facts.
**URLs:** https://data.stanford.edu/congress_text

---

## peterson2018: Peterson & Spirling (2018), Political Analysis 26(1):120–128

**Metadata: OK.** Crossref (https://api.crossref.org/works/10.1017/pan.2017.39) gives the title "Classification Accuracy as a Substantive Quantity of Interest: Measuring Polarization in Westminster Systems", authors Andrew Peterson and Arthur Spirling, *Political Analysis* 26(1), pages 120–128, issue dated January 2018, online 29 January 2018. The DOI resolves to the Cambridge article page.

**Support**

"A similar idea was used for the British Parliament by Peterson & Spirling (2018), who treated the accuracy of a party classifier as a measure of polarization in its own right."
- **Verdict: yes.**
- Abstract: "We suggest a new measurement strategy that makes innovative use of the "accuracy" of machine classifiers, i.e., the number of correct predictions made as a proportion of all predictions. In our case, the "labels" are the party identifications of the members of parliament, predicted from their speeches along with some information on debate subjects. Intuitively, when the learner is able to discriminate members in the two main Westminster parties well, we claim we are in a period of "high" polarization. By contrast, when the classifier has low accuracy … we argue parliament is in an era of "low" polarization."
- Section 1 (Motivation): "we demonstrate that machine learning "accuracy" provides an informative measurement instrument for the degree of aggregate polarization in the UK House of Commons over time."
- Same section, on how close the idea is to Gentzkow et al's: "our work is similar in spirit to recent efforts from Gentzkow, Shapiro, and Taddy (2016). Those authors also provide a method for estimating polarization from speeches." This backs up "A similar idea".
- Section 2: "Our data is essentially the entirety of the Hansard record of British parliamentary debates from 1935 to 2013."
- Optional precision: the data are House of Commons speeches only. "the British House of Commons" would be more exact than "the British Parliament". This is not an error.

**Evidence level:** full text. The publisher's HTML page showed the article body.
**URLs:** https://api.crossref.org/works/10.1017/pan.2017.39 ; https://www.cambridge.org/core/journals/political-analysis/article/classification-accuracy-as-a-substantive-quantity-of-interest-measuring-polarization-inwestminster-systems/45746D999CFCD1CB43E362392D7B2FB4

---

## lewis2026: Lewis et al (2026), Voteview: Congressional Roll-Call Votes Database

**Metadata: OK.** The Voteview data-help pages give this citation: "Lewis, Jeffrey B., Keith Poole, Howard Rosenthal, Adam Boche, Aaron Rudkin, and Luke Sonnet (2026). Voteview: Congressional Roll-Call Votes Database. https://voteview.com/". Your entry matches it exactly. The download date (5 November 2026) is your own record and cannot be checked from outside. The file still downloads from https://voteview.com/static/data/out/members/HSall_members.csv. Today's copy runs through Congress 119.

**Support**

"each speaker to their party and voting score in the Voteview member file"
- **Verdict: yes.**

"Voteview `HSall_members.csv` … joined on bioguide identifier and Congress. Party code 100 is Democratic and 200 Republican."
- **Verdict: yes.**
- data_help_members: "Quick Link (all congresses, all chambers, CSV format): https://voteview.com/static/data/out/members/HSall_members.csv"
- Same page: "congress : Integer 1+ . The number of the congress that this member's row refers to." and "bioguide_id : String. Member identifier in the Biographical Directory of Congress." and "party_code : Integer 1-9999 . Identifying code for the member's party." and "nominate_dim1 : NOMINATE first dimension estimate."
- data_help_parties, Party Codes table: "100 Democratic Party 200 Republican Party"
- Voteview "Polarization in Congress" (Lewis, 6 Oct 2026): "Note also the Democrats and Republicans are ICPSR party codes 100 and 200 respectively."
- Note: the party codes are documented on the parties help page, not the members page. The Lewis 2026 database citation covers both pages, so no change is needed.

**Evidence level:** primary documentation pages plus the data file itself.
**URLs:** https://voteview.com/articles/data_help_members ; https://voteview.com/articles/data_help_parties ; https://voteview.com/articles/party_polarization ; https://voteview.com/static/data/out/members/HSall_members.csv

---

## voteview2026: Voteview (2026), "Data - Member Ideology", 22 January 2026

**Metadata: OK, with one note.** The page title is "Data - Member Ideology" and the byline is "Voteview". It shows the date "January 22, 2026". The page's own script rewrites that date to "Originally published: August 01, 2018 · Last updated: January 22, 2026". So 22 January 2026 is the last-update date. Optional: write "updated 22 January 2026" or add "originally published 1 August 2018".

**Support**

"*DW-NOMINATE* places each member on a scale from about −1 to +1 based on how they vote with and against other members, and its first dimension is often interpreted as economic liberalism versus conservatism ([Voteview 2026](#references))."
- **Verdict: partly.** The cited page supports the first-dimension interpretation. It does not support the −1 to +1 range or the "based on how they vote" description.
- Supported, data_help_members, "Making use of Ideological Data": "We expect that most users of our data will primarily make use of the nominate_dim1 field, which reports the first dimension (often interpreted as economic liberalism-conservatism) of members as estimated by NOMINATE."
- Not on the cited page: the "−1 to +1" range. The page gives no range for nominate_dim1. In today's HSall_members.csv, nominate_dim1 runs from exactly −1.0 to 1.0, so the claim is true. It is just not stated on the cited page.
- Not on the cited page: "based on how they vote with and against other members". The Voteview About page (https://voteview.com/about) covers it: "Ideological positions are calculated using the DW-NOMINATE (Dynamic Weighted NOMINAl Three-step Estimation). … a spatial map is much like a road map--the closeness of two legislators on the map shows how similar their voting records are."
- The next sentence, "The distance between the two parties' average scores has grown over the same period", carries no citation. It is true in the Voteview data. My calculation of the Republican mean minus the Democratic mean of nominate_dim1 from HSall_members.csv gives: House 0.758 (104th Congress) → 0.910 (119th); Senate 0.653 → 0.923. Voteview's "Polarization in Congress" page publishes this series ("Difference in Party Means - first dimension"). Consider citing that page for the sentence.
- Suggested fix, either one:
  - (a) Keep the sentence and add the About page as a second Voteview reference, for example "Voteview (n.d.). 'About the project'. voteview.com/about". Then cite both pages.
  - (b) Narrow the wording to what data_help_members says: "*DW-NOMINATE* places each member on a scale using their roll-call votes, and the first dimension, which runs from −1 to +1, is often interpreted as economic liberalism versus conservatism." Even (b) still needs a source for the scale and the range, so (a) is better.

**Evidence level:** primary pages read in full, plus a check of the data file for the range.
**URLs:** https://voteview.com/articles/data_help_members ; https://voteview.com/about ; https://voteview.com/articles/party_polarization ; https://voteview.com/static/data/out/members/HSall_members.csv

---

## diermeier2012: Diermeier, Godbout, Yu & Kaufmann (2012), BJPolS 42(1):31–55

**Metadata: OK.** Crossref (https://api.crossref.org/works/10.1017/S0007123411000160) gives the title "Language and Ideology in Congress", authors Daniel Diermeier, Jean-François Godbout, Bei Yu and Stefan Kaufmann, *British Journal of Political Science* 42(1), pages 31–55. The print issue is dated January 2012; the article was published online on 23 May 2011. The DOI resolves to the Cambridge abstract page. Citing it as 2012 is standard.

**Support**

"Earlier work has classified senators by ideology from their speeches ([Diermeier et al 2012](#references))"
- **Verdict: yes**, at the level of detail the sentence claims.
- Abstract (Cambridge page): "Legislative speech records from the 101st to 108th Congresses of the US Senate are analysed to study political ideologies. A widely-used text classification algorithm – Support Vector Machines (SVM) – allows the extraction of terms that are most indicative of conservative and liberal positions in legislative speeches and the prediction of senators' ideological positions, with a 92 per cent level of accuracy."
- Caveat: I could not get the full text, because it is paywalled and I found no open copy. Secondary descriptions say that only senators labelled "extreme" by roll-call scores were used, and that moderates were treated separately. I could not confirm this from the paper itself. The post's sentence gives no specifics such as the 92% figure or which senators were included, so the abstract is enough to support it. Do not add details such as "92% accuracy across all senators" without the full text. As far as the abstract shows, the 92% may apply only to the extreme-senator subset.

**Evidence level:** abstract only (publisher page). That is enough for this general sentence.
**URLs:** https://api.crossref.org/works/10.1017/S0007123411000160 ; https://www.cambridge.org/core/journals/british-journal-of-political-science/article/abs/language-and-ideology-in-congress/1063F5509BC2ABC3F9A0E164E58157EE

---

## AP news link: "Democrats win control of U.S. House, in major rebuke to Trump" (AP, on PBS News)

**Metadata: OK.** The URL resolves (HTTP 200) to the PBS News page "Democrats win control of U.S. House, in major rebuke to Trump". The byline is Jill Colvin, Mary Clare Jalonick and Will Weissert, all Associated Press. The article metadata shows it was published 2026-11-04T01:27:26-05:00 ("Published on Nov 4, 2026 1:27 AM EST", updated 1:48 AM EST). The dateline is "WASHINGTON (AP)". The link text "Associated Press, 4 November 2026" is correct. Optional: add "via PBS News", since the URL is PBS.

**Support**

"On 3 November 2026, Democrats won control of both the House and the Senate"
- **Verdict: yes.**
- "WASHINGTON (AP) — Democrats have won control of the U.S. House in addition to the U.S. Senate, delivering a shockingly decisive rebuke of Republican governance in Washington"
- "The midterm elections that came to a close Tuesday". 3 November 2026 is a Tuesday.
- Note: the URL slug and the headline mention only the House. The Senate result is in the first sentence of the story, and the page links a companion piece, "Democrats take control of the Senate after winning key midterm races". Readers who only see the headline may wonder, but the sentence as written is supported.

**Evidence level:** full article text.
**URLs:** https://www.pbs.org/newshour/politics/democrats-win-control-of-the-u-s-house

---

# 3. Checking pass B

# Citation check results, batch B (checked 2026-11-06)

Sources: lauderdale2016, warner2025, xiao2024, nosek2018, akiba2019, hoerl1970.
Metadata was checked against Crossref (api.crossref.org/works/<doi>) and the publisher page. Every DOI was resolved with `curl -I https://doi.org/<doi>`.
Local copies of the downloaded files are in
/tmp/claude-1000/-home-kevin-repos-politics/cccb3500-5f4b-4d91-862a-fe43ddee0c94/scratchpad/dlB/
(the PDFs plus the text extracted from them with pypdf).

| Source | Metadata ok? | Support | Evidence level |
|---|---|---|---|
| lauderdale2016 | Yes | Partly: 0.46 is right, but the wording needs narrowing | Full text (accepted manuscript) + published abstract |
| warner2025 | Yes (post's 14 authors match the PDF; Crossref/ACL metadata drop Nathan Cooper) | Yes | Full text (ACL Anthology PDF) |
| xiao2024 | Yes | Yes (Table 5 BGE (base) row = bge-base-en-v1.5 model-card row) | Full text (arXiv v5, SIGIR '24 camera-ready layout) + model card |
| nosek2018 | Yes | Yes, with a small caveat on wording | Full text (PMC, via WebFetch) |
| akiba2019 | Yes | Yes for Optuna. The paper names TPE but does not describe it | Full text (arXiv preprint 1907.10902v1) |
| hoerl1970 | Yes | Yes | Full text (scan of the original article) |

---

## lauderdale2016

**Citing sentences**
1. "...estimated senators' positions from speech, finding moderate agreement with positions estimated from votes within each party ([Lauderdale & Herzog 2016])."
2. "[Lauderdale & Herzog (2016)] reported a within-party correlation of 0.46 between speech-based and vote-based positions for senators, using different methods and their own vote-based scale, which is close to what I found here."

**Metadata: OK.** Crossref: Lauderdale, Benjamin E.; Herzog, Alexander. "Measuring Political Positions from Legislative Speech". *Political Analysis* 24(3):374–394. Issued 2016, online 4 Jan 2017. The DOI 10.1093/pan/mpw017 redirects to cambridge.org (S1047198700014091). The Cambridge page gives vol 24, issue 3 (Summer 2016), pp. 374–394. The authors agree across all sources.

**Support: partly.** The number 0.46 is correct, and the post rightly notes that the methods and the vote scale differ. Three details are off or missing.

- Abstract (accepted MS p. 1; the Cambridge abstract matches): "In the US Senate, we estimate a dimension that has moderate within-party correlations with scales based on roll-call votes and campaign donation patterns, however we observe greater overlap across parties in speech positions than roll-call positions and partisan polarization in speeches varies more clearly in response to major political events."
- Section 5.1 "Speeches, Roll-Calls, and Donations" (accepted MS p. 25): "For roll-call votes, we fit a standard Bayesian IRT model to all votes over the same period as our speeches. ... If we calculate correlations between within-party variation in these three scores, we find that roll-call scores are correlated with speech scores at ρ = 0.46, while donor scores are correlated with roll-call scores at ρ = 0.57 and with speech scores at ρ = 0.55."
- Footnote 13 (p. 25): "The largest difference (between the 0.46 correlation of roll-calls and speech scores and the 0.57 correlation between roll-call and donor scores) has p = 0.05, ignoring the multiple comparisons."
- Section 5 (p. 23): "we use all debates from January 1995 to the end of October 2014, covering the 104th to the 113th Senate. We fit a model where senators are assumed to have constant positions."
- Section 1 (p. 2): "we compare the estimates from our model to existing scaling methods for US Senators based on roll-call votes (Poole and Rosenthal 1985; Clinton, Jackman and Rivers 2004) and campaign donations (Bonica 2014). While estimates from all three methods are positively and similarly correlated within as well as across parties..."
- Section 1 (p. 2) on method: "Like any unsupervised scaling method, the substantive meaning of the legislator-specific ..." The speech scale is unsupervised (Wordshoal) and was not trained to predict votes.

The issues:
- (a) **"within each party"** (sentence 1). The paper reports a single correlation of "within-party variation", which appears to pool both parties after removing party differences. It does not give a correlation for each party separately. "Moderate" is the authors' own word, so it is fair.
- (b) **The vote-based scale** is the authors' own Bayesian IRT model, not DW-NOMINATE. The post already says "their own vote-based scale", which is correct.
- (c) **"close to what I found here."** Their 0.46 is one pooled figure for senators only, 104th–113th Senate, with one position per senator for the whole period. It comes from an unsupervised speech scale. The post's 0.46 and 0.48 are separate Democratic and Republican correlations for House and Senate member-Congresses, from a supervised prediction of DW-NOMINATE. The numbers are similar, but the comparison is loose. Saying so in a few words would be safer.

**Suggested wording**
1. "...and estimated senators' positions from speech, finding a moderate within-party correlation with positions estimated from roll-call votes ([Lauderdale & Herzog 2016])."
2. "[Lauderdale & Herzog (2016)] reported a within-party correlation of 0.46 between speech-based and roll-call-based positions for senators from 1995 to 2014. That was a single figure for both parties, from an unsupervised speech scale and their own roll-call scale, so it is not directly comparable, but it is of a similar size to what I found here."

**Evidence level:** full text of the accepted manuscript, LSE Research Online eprint 66498, version 7, 42 pp. The abstract of the published version was checked on Cambridge Core. I did not read the full published typeset version, so the page numbers above are manuscript pages.

**URLs read:**
- https://api.crossref.org/works/10.1093/pan/mpw017
- https://researchonline.lse.ac.uk/id/eprint/66498
- https://researchonline.lse.ac.uk/id/eprint/66498/7/Lauderdale_Measuring%20political.pdf
- https://www.cambridge.org/core/journals/political-analysis/article/abs/measuring-political-positions-from-legislative-speech/35D8B53C4B7367185325C25BBE5F42B4

---

## warner2025

**Citing sentences**
1. "The main model is ModernBERT, a recent language model ([Warner et al 2025]) fine-tuned separately for each Congress..."
2. "**Language model:** `answerdotai/ModernBERT-base` ([Warner et al 2025]) fine-tuned for two-class classification."

**Metadata: OK.**
- Title, venue (ACL 2025 Long Papers), pages 2526–2547, DOI and year all match Crossref and the ACL Anthology.
- The author list differs between sources:
  - Crossref and the ACL Anthology BibTeX list **13** authors. They omit **Nathan Cooper** and give "Griffin Thomas Adams".
  - The PDF's author block lists **14** authors: "Benjamin Warner, Antoine Chaffin, Benjamin Clavié, Orion Weller, Oskar Hallström, Said Taghadouini, Alexis Gallagher, Raja Biswas, Faisal Ladhak, Tom Aarsen, Nathan Cooper, Griffin Adams, Jeremy Howard, Iacopo Poli".
  - The post's list matches the PDF, which is correct. Optionally, add a BibTeX comment that the Crossref and Anthology metadata omit Cooper.
- The arXiv preprint (2412.13663) was first posted on 18 Dec 2024.

**Support: yes.**
- PDF header: "Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 2526–2547".
- Abstract: "Encoder-only transformer models such as BERT offer a great performance-size tradeoff for retrieval and classification tasks ... In this paper, we introduce ModernBERT, bringing modern model optimizations to encoder-only models..."
- §1 Contributions: "We present ModernBERT, a modernized encoder-only transformer model ... We release two models, ModernBERT-base and ModernBERT-large..."
- §2.2.2: "MLM We follow the Masked Language Modeling (MLM) setup used by MosaicBERT".
- Model card (huggingface.co/answerdotai/ModernBERT-base): "ModernBERT is a modernized bidirectional encoder-only Transformer model (BERT-style) pre-trained on 2 trillion tokens of English and code data". It lists "ModernBERT-base - 22 layers, 149 million parameters" and points to arXiv 2412.13663.

"A recent language model" is fair: it is a masked-language-model encoder released in Dec 2024 and published in 2025. The optional wording below is more precise and avoids readers assuming a chat or generative LLM.

**Suggested wording (optional):** "ModernBERT, a recent encoder-only language model ([Warner et al 2025])".

**Evidence level:** full text (ACL Anthology PDF, 22 pp.) and the model card.

**URLs read:**
- https://api.crossref.org/works/10.18653/v1/2025.acl-long.127
- https://aclanthology.org/2025.acl-long.127.pdf
- https://aclanthology.org/2025.acl-long.127.bib
- https://huggingface.co/answerdotai/ModernBERT-base/raw/main/README.md
- https://export.arxiv.org/api/query?id_list=2412.13663

---

## xiao2024

**Citing sentences**
1. "...using a sentence-embedding model ([Xiao et al 2024]), and averaged them."
2. "...embedded with `BAAI/bge-base-en-v1.5` ([Xiao et al 2024]), truncated at 512 tokens and normalised..."

**Metadata: OK.** Crossref: Xiao S, Liu Z, Zhang P, Muennighoff N, Lian D, Nie J-Y. "C-Pack: Packed Resources For General Chinese Embeddings". SIGIR '24, pp. 641–649, issued 10 Jul 2024. The DOI resolves to dl.acm.org. The six authors match the arXiv v5 PDF.

The BGE model card's own citation block uses the old arXiv title, "C-Pack: Packaged Resources To Advance General Chinese Embedding" (2023, 4 authors). The post's SIGIR title is the right one for the DOI cited.

**Support: yes.** The paper covers the English BGE models, and its English results table matches the v1.5 base model exactly.

- Abstract: "Along with our resources on general Chinese embedding, we release our data and models for English text embeddings. The English models also achieve state-of-the-art performance on the MTEB benchmark..."
- §4.1 (p. 7): "Using the same recipe as the Chinese models, we also train a set of English text embedding models presented in Table 5. ... At the time of public release, our English BGE models achieved the state-of-the-art performance on the English MTEB benchmark [35] across its 56 datasets."
- Table 5 (p. 8), "Performance of English Models on MTEB": "BGE (base) 768 63.55 53.25 45.77 86.55 58.86 82.4 31.07 75.53".
- The model card for BAAI/bge-base-en-v1.5 has the identical row: "[BAAI/bge-base-en-v1.5] | 768 | 512 | 63.55 | 53.25 | 45.77 | 86.55 | 58.86 | 82.4 | 31.07 | 75.53". The original bge-base-en scores 63.36 on the card. So the paper's English base model is the v1.5 model, although the paper never writes "v1.5".
- Model card: "release `bge-*-v1.5` embedding model to alleviate the issue of the similarity distribution". Its MTEB table has a "Sequence Length" of 512, and its usage examples call `model.encode(..., normalize_embeddings=True)`. These support "truncated at 512 tokens and normalised". The 512 limit is documented on the card, not in the paper.

**Suggested wording:** none needed. Optionally, cite the model card next to the model ID for the 512-token limit and the normalisation, e.g. "(Xiao et al 2024; model card at huggingface.co/BAAI/bge-base-en-v1.5)".

**Evidence level:** full text of arXiv 2309.07597v5, 9 pp., in the SIGIR '24 layout ("SIGIR '24, July 14–18, 2024, Washington, DC, USA" in the running header), plus the model card. I did not open the ACM DL version itself.

**URLs read:**
- https://api.crossref.org/works/10.1145/3626772.3657878
- https://arxiv.org/pdf/2309.07597
- https://huggingface.co/BAAI/bge-base-en-v1.5/raw/main/README.md

---

## nosek2018

**Citing sentence:** "So I wrote down the questions, the tests, and what would count as a yes before training any model... Writing tests down first is what separates a prediction from an explanation found afterwards ([Nosek et al 2018])."

**Metadata: OK.** Crossref and PMC: Nosek BA, Ebersole CR, DeHaven AC, Mellor DT. "The preregistration revolution". *PNAS* 115(11):2600–2606. Online 12 Mar 2018, print 13 Mar 2018. The DOI resolves to pnas.org.

**Support: yes.** "Explanation found afterwards" matches the paper's "postdiction".
- Abstract: "Progress in science relies in part on generating hypotheses with existing observations and testing hypotheses with new observations. This distinction between postdiction and prediction is appreciated conceptually but is not respected in practice. ... An effective solution is to define the research questions and analysis plan before observing the research outcomes—a process called preregistration. Preregistration distinguishes analyses and outcomes that result from predictions from those that result from postdictions."
- Introduction: "In postdiction, the data are already known and the postdiction is generated to explain why they occurred."
- Section "Preregistration Distinguishes Prediction and Postdiction": "With preregistration, prediction is achieved because selection of tests is not influenced by the observed data"; "In principle, preregistration can establish a bright line between prediction and postdiction."; "Preregistration does not favor prediction over postdiction; its purpose is to make clear which is which."

**Caveat:**
- The paper calls preregistration "an effective solution". The bright line holds "in principle".
- Challenge 3 warns that once data have been observed, "there are inevitable risks for blinding." Here the Record and the earlier results were known before the plan was written, though no model had been trained.
- The post's sentence is fine as a paraphrase. A slightly more faithful version is below.

**Suggested wording (optional):** "Writing the tests down first is what lets a reader tell a prediction from an explanation found afterwards ([Nosek et al 2018])."

**Evidence level:** full text read on PMC through WebFetch, which returns quotes in fragments of at most 125 characters. The quotes above are those fragments rejoined. The abstract sentence was confirmed as exact by a web search hit on PubMed and PMC.

**URLs read:**
- https://api.crossref.org/works/10.1073/pnas.1708274114
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/

---

## akiba2019

**Citing sentence:** "The settings came from a 15-trial search with Optuna's TPE sampler ([Akiba et al 2019]) on the 108th Congress..."

**Metadata: OK.** Crossref: title "Optuna", subtitle "A Next-generation Hyperparameter Optimization Framework". Akiba T, Sano S, Yanase T, Ohta T, Koyama M. KDD '19, pp. 2623–2631, 25 Jul 2019. The DOI resolves to dl.acm.org. The authors match the arXiv preprint.

**Support: yes for Optuna and for Optuna offering TPE.** The paper names TPE and benchmarks it, but does not describe how TPE works. TPE itself is Bergstra et al. 2011, the paper's ref [6].
- §1: "Hyperopt [1] employs tree-structured Parzen estimator (TPE) [6]."
- §3.1 "Sampling Methods on Dynamically Constructed Parameter Space" (p. 4): "The independent sampling is not necessarily a naive option, because some sampling algorithms like TPE [6] are known to perform well even without using the parameter correlations ... Our Optuna features both, and it can handle various independent sampling methods including TPE as well as relational sampling methods like CMA-ES."
- §5.1 (p. 6): "For TPE+CMA-ES, we used TPE for the first 40 steps and used CMA-ES for the rest."
- Ref [6] in the paper: James Bergstra, Rémi Bardenet, Yoshua Bengio, and Balázs Kégl (2011), "Algorithms for hyper-parameter optimization" (NeurIPS).

**Suggested wording:** the sentence is fine as written, since the citation is attached to Optuna. Optionally add Bergstra et al. 2011 for TPE itself: "with Optuna's ([Akiba et al 2019]) tree-structured Parzen estimator (TPE) sampler ([Bergstra et al 2011])". That would need a new reference, checked separately.

**Evidence level:** full text of the arXiv preprint 1907.10902v1, 10 pp., posted 25 Jul 2019. I did not open the ACM KDD version; its title, authors and pages agree with Crossref.

**URLs read:**
- https://api.crossref.org/works/10.1145/3292500.3330701
- https://arxiv.org/pdf/1907.10902
- https://export.arxiv.org/api/query?id_list=1907.10902

---

## hoerl1970

**Citing sentence:** "A ridge regression ([Hoerl & Kennard 1970]) then predicted the voting score from that average."

**Metadata: OK.** Crossref: Hoerl, Arthur E.; Kennard, Robert W. "Ridge Regression: Biased Estimation for Nonorthogonal Problems". *Technometrics* 12(1):55–67, Feb 1970. The DOI resolves to tandfonline.com. The scan's header reads "TECHNOMETRICS VOL. 12, No. 1 FEBRUARY 1970" with pp. 55–67. The JSTOR copy has a second DOI, 10.2307/1267351; the T&F DOI used in the post is fine.

**Support: yes.** This is the paper that named the method.
- Abstract (p. 55): "Proposed is an estimation procedure based on adding small positive quantities to the diagonal of X'X. Introduced is the ridge trace..."
- §2 "Ridge Regression" (p. 56–57): "A. E. Hoerl first suggested in 1962 ... that to control the inflation and general instability associated with the least squares estimates, one can use β* = [X'X + kI]⁻¹X'Y; k ≥ 0 ... For this reason, estimation and analysis built around (2.1) has been labeled 'ridge regression.'"

(The quotes come from OCR text, with the obvious OCR errors corrected.)

**Suggested wording:** none.

**Evidence level:** full text, a 13-page scan of the original article hosted in the stat.cmu.edu Technometrics archive. The T&F page returned 403.

**URLs read:**
- https://api.crossref.org/works/10.1080/00401706.1970.10488634
- https://www.stat.cmu.edu/technometrics/70-79/VOL-12-01/v1201055.pdf
- https://www.tandfonline.com/doi/abs/10.1080/00401706.1970.10488634 (403)
