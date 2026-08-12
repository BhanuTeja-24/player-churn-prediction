# -*- coding: utf-8 -*-
"""Body text for the churn-prediction dissertation.

Every figure named here exists in outputs/figures and every number quoted is
taken from outputs/tables. Every reference in REFERENCES was checked against a
live DOI or publisher record before being included.

Conventions:
  * plain string            -> body paragraph
  * '3.1 Some Title'        -> Heading 2
  * '[[FIG:name.png|cap]]'  -> figure from outputs/figures with numbered caption
  * '[[TAB:key|cap]]'       -> table from TABLES below with numbered caption
"""

# TODO: replace with the student's full name exactly as registered before submitting.
AUTHOR = 'Bhanu'

TITLE = ('Player Churn Prediction and Engagement Optimisation in Online Gaming '
         'Platforms Using Machine Learning')
SUBTITLE = ('An explainability and fairness analysis of behavioural telemetry '
            'from three commercial games')

# --------------------------------------------------------------- tables -----

TABLES = {
    'datasets': [
        ['Game', 'Description', 'Events', 'Players', 'Span (days)'],
        ['game1', 'Dodge the Mud - Android casual action', '153,929', '25,956', '496'],
        ['game2', 'Casual racing, iOS and Android, with purchases', '7,620,167', '79,436', '107'],
        ['game3', 'TagPro - web capture-the-flag, match outcomes', '3,516,753', '91,094', '213'],
    ],
    'etl_check': [
        ['Quantity', 'Reported by Kim et al. [1]', 'Extracted by this project', 'Difference'],
        ['Total records', '10,874,958', '11,290,849', '+3.8%'],
        ['Total players', '193,443', '196,486', '+1.6%'],
    ],
    'cohorts': [
        ['Game', 'Players', 'Churners', 'Churn rate', 'Median events in OP'],
        ['game1', '25,121', '23,261', '92.6%', '2'],
        ['game2', '79,410', '59,960', '75.5%', '31'],
        ['game3', '24,128', '14,477', '60.0%', '4'],
    ],
    'results': [
        ['Game', 'Model', 'ROC-AUC', 'PR-AUC (retained)', 'Base rate', 'Lift', 'Balanced acc.'],
        ['game1', 'LSTM', '0.7834', '0.3538', '0.0740', '4.78x', '0.5622'],
        ['game1', 'Logistic Regression', '0.7736', '0.3372', '0.0740', '4.56x', '0.5519'],
        ['game1', 'XGBoost', '0.7418', '0.3008', '0.0740', '4.06x', '0.5838'],
        ['game1', 'Random Forest', '0.7280', '0.2946', '0.0740', '3.98x', '0.5712'],
        ['game2', 'Logistic Regression', '0.7585', '0.5762', '0.2449', '2.35x', '0.6216'],
        ['game2', 'XGBoost', '0.7581', '0.5788', '0.2449', '2.36x', '0.6429'],
        ['game2', 'Random Forest', '0.7574', '0.5770', '0.2449', '2.36x', '0.6327'],
        ['game2', 'LSTM', '0.7441', '0.5679', '0.2449', '2.32x', '0.6296'],
        ['game3', 'Logistic Regression', '0.8056', '0.7689', '0.3999', '1.92x', '0.7262'],
        ['game3', 'LSTM', '0.8053', '0.7743', '0.3999', '1.94x', '0.7291'],
        ['game3', 'Random Forest', '0.8034', '0.7759', '0.3999', '1.94x', '0.7234'],
        ['game3', 'XGBoost', '0.8033', '0.7750', '0.3999', '1.94x', '0.7335'],
    ],
    'shap_game2': [
        ['Feature', 'Mean absolute SHAP', 'Pushes towards'],
        ['win_ratio', '0.853', 'Churn'],
        ['attempt_count', '0.534', 'Retention'],
        ['fail_ratio', '0.418', 'Churn'],
        ['quit_ratio', '0.388', 'Churn'],
        ['complete_ratio', '0.353', 'Retention'],
        ['day0_plays', '0.282', 'Churn'],
        ['mean_outcome_std', '0.276', 'Retention'],
    ],
    'fairness': [
        ['Game', 'Attribute', 'AUC gap', 'Worst-served group', 'Worst AUC', 'Best AUC'],
        ['game1', 'engagement_tier', '0.250', 'light players', '0.521', '0.771'],
        ['game3', 'engagement_tier', '0.242', 'light players', '0.575', '0.817'],
        ['game3', 'skill_tier', '0.180', 'low skill', '0.648', '0.828'],
        ['game2', 'skill_tier', '0.116', 'high skill', '0.665', '0.781'],
        ['game2', 'spend_tier', '0.107', 'low spenders', '0.675', '0.782'],
        ['game2', 'engagement_tier', '0.097', 'medium', '0.661', '0.758'],
        ['game2', 'device_family', '0.057', 'iPod', '0.722', '0.779'],
        ['game1', 'skill_tier', '0.054', 'mid skill', '0.736', '0.790'],
        ['game2', 'platform', '0.006', 'Android', '0.755', '0.761'],
    ],
    'sensitivity': [
        ['OP (days)', 'CP (days)', 'Players', 'Labelled churn rate', 'ROC-AUC', 'PR-AUC (retained)'],
        ['3', '7', '79,416', '71.1%', '0.7417', '0.5907'],
        ['5', '10', '79,410', '75.5%', '0.7581', '0.5788'],
        ['7', '14', '79,397', '78.3%', '0.7566', '0.5542'],
        ['5', '30', '79,349', '70.2%', '0.7530', '0.6248'],
    ],
}

# ------------------------------------------------------------- abstract -----

ABSTRACT = [
    'Player retention is the central economic problem of free-to-play game '
    'operation: revenue depends less on acquiring players than on preventing '
    'them from leaving. This project addresses the prediction of player churn '
    'from behavioural telemetry, and asks a question that the prediction '
    'literature has largely left aside - not merely whether churn can be '
    'predicted, but which in-game systems drive it, and whether the resulting '
    'model serves all kinds of player equally well.',

    'The literature reviewed covers three strands. Game-analytics work '
    'established that churn is predictable from generic behavioural features '
    'such as session frequency, playtime and inter-session gaps, and that a '
    'churn label must be constructed rather than observed because casual games '
    'carry no subscription to cancel. Explainability research supplied Shapley '
    'additive explanations as a means of attributing individual predictions to '
    'features with a signed, per-player contribution. Algorithmic-fairness '
    'research supplied the subgroup-auditing methodology, though almost always '
    'applied to protected demographic attributes that behavioural game logs do '
    'not contain.',

    'The implementation processes 11,290,849 raw events from 196,486 players '
    'across three commercial games released under a CC-BY licence alongside a '
    'peer-reviewed study. An extract-transform-load pipeline was built that '
    'solves two genuine defects in the published archives: seven of one game\'s '
    'eight archive parts use the Deflate64 compression method, which the Python '
    'standard library cannot decompress, and a second game\'s player file is '
    'delivered at its full declared size but with structurally truncated JSON. '
    'Churn was labelled using an explicit observation period and churn '
    'prediction period, extended with two censoring guards that the source study '
    'leaves implicit. Logistic regression, random forest, XGBoost and a long '
    'short-term memory network were compared, interpreted with Shapley values '
    'and audited across behavioural and contextual subgroups.',

    'Three findings emerge. First, no architecture wins universally: the '
    'sequence model leads on one game while penalised logistic regression leads '
    'on the other two, and on one game the spread across all four models is '
    '0.0023 area under the receiver operating characteristic curve - a '
    'defensible negative result favouring interpretable models in production. '
    'Second, on the racing game a high win ratio pushes predictions towards '
    'churn while attempt count and completion ratio protect retention, placing '
    'the flow-channel hypothesis directly in commercial telemetry: winning too '
    'easily is as much a retention risk as losing too often. Third, and most '
    'consequentially, the model is markedly weaker for low-engagement players, '
    'with an area-under-curve gap of 0.250 on one game and 0.242 on another. '
    'The retention system performs worst for precisely the casual majority most '
    'at risk of leaving, a disparity that replicates across two independent '
    'games and that a conventional accuracy-led evaluation would not reveal.',
]

ACKNOWLEDGEMENTS = [
    'The author thanks the supervisory team for their guidance throughout this '
    'project, and Kim, Choi, Lee and Rhee, whose decision to release the raw '
    'play logs underpinning their 2017 study under an open licence made this '
    'independent analysis possible. Open data release remains uncommon in '
    'commercial game analytics, and this project would not have existed without '
    'it.',
]

# ------------------------------------------------------------- chapter 1 ----

CH1_INTRO = [
    'The free-to-play business model has made player retention the decisive '
    'commercial variable in the games industry. A premium title collects '
    'revenue at the point of sale; a free-to-play title collects nothing until '
    'a player has engaged long enough to spend, making the departure of a '
    'player - churn - the primary threat to revenue.',

    'This project builds and evaluates a churn-prediction system over '
    'behavioural telemetry from three commercial games, extending it in two '
    'directions the literature treats as secondary: explaining which in-game '
    'systems drive the predictions, and auditing whether the model performs '
    'equally well across different kinds of player.',
]

CH1_PROBLEM = [
    'The problem addressed is the early identification of players who will stop '
    'playing, together with the game systems associated with their departure. '
    'In a free-to-play title there is no subscription to cancel and so no '
    'moment at which a player announces departure; churn must be inferred from '
    'absence of activity. That inference is the first difficulty, because '
    'absence is ambiguous - a player missing from the logs may have left, may '
    'be taking a break, or may return after the window closes.',

    'Three parties are affected. Studios commercially, since retention '
    'determines revenue. Players experientially, because retention systems '
    'shape the game they are offered: difficulty curves, reward schedules and '
    'notification timing are increasingly tuned by models of this kind. Design '
    'teams professionally, because a model identifying which systems push '
    'players away is actionable in a way an aggregate retention figure is '
    'not.',

    'The problem occurs at the earliest stage of the player lifecycle. Most '
    'casual players leave within days of installation, so a prediction is '
    'useful only if made from a very short window of behaviour - a median of '
    'two events on one game here. The alternative is untargeted intervention: '
    'contacting everyone, which is expensive and degrades the experience of '
    'players who were never leaving, or contacting no one.',
]

CH1_OBJECTIVES = [
    'The project set six objectives:',
    'O1. Construct a reproducible extract-transform-load pipeline converting '
    'the raw published archives into tidy event tables, validated against the '
    'record counts reported in the source study.',
    'O2. Implement a parameterised churn label from an explicit observation and '
    'churn prediction period, strengthened with censoring guards preventing the '
    'model learning artefacts of the logging window.',
    'O3. Engineer behavioural features computed strictly within the observation '
    'period, so no label-window information leaks into the model.',
    'O4. Train and compare interpretable, ensemble and sequence classifiers '
    'under metrics appropriate to a heavily imbalanced target.',
    'O5. Apply Shapley additive explanations to identify which in-game systems '
    'are associated with retention and which with departure, interpreting the '
    'result against established game-design theory.',
    'O6. Audit the model for performance disparities across player subgroups, '
    'and report honestly which fairness questions this data can and cannot '
    'answer.',
]

CH1_METHODOLOGY = [
    'Design. The system is a linear pipeline of independently testable stages - '
    'extraction, labelling, feature engineering, modelling, explanation and '
    'audit - each writing a persistent artefact. This was chosen over a '
    'monolithic script because extraction is expensive, and persisting its '
    'output lets the labelling parameters vary without repeating it.',

    'Testing and Evaluation. Extracted record and player counts are compared '
    'against the totals published by Kim et al. [1] - an external reference a '
    'self-consistent pipeline could not otherwise provide. Evaluation '
    'deliberately avoids accuracy, uninformative on a target between 60% and '
    '93% churn, in favour of the ranking and lift metrics justified in Chapter '
    '3, following Saito and Rehmsmeier [17]. Stability is probed by re-running '
    'under four labelling configurations.',

    'Project Management. Work was organised into six sequential sprints '
    'matching the six objectives, tracked on a Kanban board and bounded where a '
    'durable artefact was produced, so progress was measured by output rather '
    'than elapsed effort (Appendix B). The extraction sprint overran '
    'substantially because of the two archive defects in Chapter 3; contingency '
    'came from an optional supplementary study, which was descoped.',

    'Technologies and Processes. Python hosts the whole required toolchain: '
    'scikit-learn [21], XGBoost [15], PyTorch [22] and the reference SHAP '
    'implementation [11]. Columnar Parquet storage was chosen for intermediate '
    'artefacts because the event tables exceed eleven million rows. Chapter 2 '
    'justifies these choices.',
]

CH1_LEGAL = [
    'Legal. The data is published under a Creative Commons Attribution 4.0 '
    'licence [2] permitting derivative analysis subject to attribution, which '
    'is given throughout. The raw archives are excluded from the submitted '
    'repository to avoid redistributing 853 megabytes of third-party data.',

    'Social and Ethical. Players appear only as opaque identifiers, which '
    'removes the most acute privacy risk but not all ethical concern. A churn '
    'model is not a neutral observation instrument - it is built to be acted '
    'upon, and the actions it supports include targeted incentives and '
    'difficulty adjustment. Where such a model performs unevenly across player '
    'groups, intervention budgets are allocated unevenly too, which is the '
    'concern motivating the fairness audit.',

    'Professional. All claims are reproducible from the submitted code and all '
    'cited material was verified. One incident deserves recording: during '
    'exploratory work an automated tool proposed a dataset that did not exist, '
    'with plausible record counts and provenance claims. It was checked, found '
    'fabricated, and discarded in favour of the verified source used here. '
    'Every reference was subsequently confirmed against a live publisher record '
    'or digital object identifier.',
]

CH1_BACKGROUND = [
    'Free-to-play games earn from a small minority of paying players, making '
    'the size and longevity of the active population the determinant of '
    'commercial success. The behavioural traces they produce - session starts, '
    'level attempts, purchases, match outcomes - are recorded at a granularity '
    'that makes statistical modelling of departure feasible.',

    'Two properties shape everything that follows: churn is unobserved and must '
    'be defined, so different definitions yield different labels and different '
    'measured performance; and the target is severely imbalanced, because most '
    'casual players leave almost immediately.',
]

CH1_STRUCTURE = [
    'Chapter 2 reviews the churn-prediction, explainability and fairness '
    'literature, then justifies the technologies selected. Chapter 3 describes '
    'the implementation, including the two archive defects solved before any '
    'analysis was possible, the churn label and its guards, the feature set and '
    'the four model families. Chapter 4 evaluates the results and positions '
    'them against related work. Chapter 5 concludes, sets out future work and '
    'reflects on the project.',
]

# ------------------------------------------------------------- chapter 2 ----

CH2_INTRO = [
    'This chapter reviews the research informing the project and the '
    'technologies available to implement it, across three strands - churn '
    'prediction, explainability and algorithmic fairness - concluding with the '
    'gap addressed.',
]

CH2_LIT = [
    'Churn prediction in games. Hadiji et al. [3] formalised churn for '
    'free-to-play titles and argued prediction should rest on generic '
    'behavioural features - playtime, session length, inter-session gaps - '
    'rather than game-specific design variables, since a model built on level '
    'identifiers or currency names cannot transfer between titles while one '
    'built on temporal engagement patterns can. This project adopts their '
    'position for its core feature set, departing from it only where a game '
    'exposes genuinely informative outcome data, on the grounds that '
    'transferability is not the only virtue.',

    'Runge et al. [4] approached the same problem commercially, restricting '
    'attention to high-value players and evaluating not prediction quality but '
    'the business impact of acting on it. Their finding that contact shortly '
    'before the predicted churn event improves campaign effectiveness '
    'establishes that a churn model\'s practical value lies in its timing and '
    'ranking of players, not its classification accuracy - which motivates the '
    'ranking-oriented metrics adopted here. Their restriction to high-value '
    'players is a limitation this project inverts: the fairness audit '
    'concentrates on precisely the low-engagement players such a filter '
    'excludes.',

    'Kim et al. [1] supply both the methodological anchor and the data. Their '
    'central contribution is a parameterised churn definition: an observation '
    'period during which behaviour is measured, and a churn prediction period '
    'during which the absence of activity defines a churner. Because both are '
    'explicit parameters, their influence can be measured rather than assumed - '
    'a substantial improvement over the arbitrary fixed-threshold definitions '
    'common elsewhere. They compare five algorithms across three games, finding '
    'the sequence model leads on one title and gradient boosting on the other '
    'two, with small differences overall. The weakness their study leaves open, '
    'and the opening this project takes, is that it reports which features are '
    'important but not in which direction they act, and does not examine '
    'whether performance is uniform across players.',

    'Bertens et al. [5] extended churn modelling with survival ensembles '
    'predicting not only whether a player will leave but when, and Viljanen et '
    'al. [7] made the survival framing explicit, arguing playtime is a censored '
    'quantity and should be modelled as such. Their critique matters here: a '
    'binary label from a fixed window discards timing information and is '
    'sensitive to where the boundary falls. This project retains the binary '
    'framing for comparability with [1], but takes the censoring critique '
    'seriously enough to add the two guards described in Chapter 3 and to test '
    'window sensitivity empirically rather than assert robustness.',

    'Li et al. [6] provide the closest work to this project\'s central '
    'interpretive finding, arguing that churn is driven substantially by '
    'difficulty mismatch and building a difficulty-aware prediction and '
    'intervention framework on that basis. Where they build difficulty into the '
    'model by design, the analysis here recovers a difficulty effect from '
    'explanation of a model given no such structure.',

    'Game-design theory. The interpretation of that difficulty effect rests on '
    'flow theory. Csikszentmihalyi [8] characterises optimal experience as a '
    'channel between anxiety and boredom in which challenge matches skill; '
    'experience degrades when challenge is too high and, critically here, '
    'equally when too low. Sweetser and Wyeth [9] operationalised this as the '
    'GameFlow model, in which challenge and skill form one of eight elements of '
    'player enjoyment. Ryan et al. [10] offer a complementary '
    'self-determination account, under which trivially easy play undermines '
    'competence satisfaction because success carries no information about '
    'ability. These theories are usually evaluated through self-report; the '
    'contribution available here is to test whether their prediction appears in '
    'large-scale telemetry.',

    'Explainability. Lundberg and Lee [11] introduced Shapley additive '
    'explanations, unifying earlier attribution methods under a game-theoretic '
    'framework with uniqueness guarantees, and Lundberg et al. [12] later '
    'supplied an exact polynomial-time algorithm for tree ensembles. What '
    'matters here is that Shapley values are signed and per-player: they state '
    'not merely that a feature mattered but in which direction it pushed a '
    'prediction. Single-feature importance rankings cannot express this, and '
    'Chapter 4\'s principal interpretive finding is invisible without it. Rudin '
    '[13] counters that post-hoc explanation of black-box models is unreliable '
    'for high-stakes decisions and that inherently interpretable models should '
    'be preferred. That critique is taken seriously in two ways: explanations '
    'are computed for a penalised linear model as well as tree ensembles, and '
    'Chapter 4 finds the linear model competitive on all three games.',

    'Fairness. Hardt et al. [18] formalised equalised odds and equality of '
    'opportunity, establishing that a classifier can satisfy demographic parity '
    'while still failing a subgroup badly. Mehrabi et al. [19] survey the '
    'resulting taxonomy of bias sources and mitigations. Buolamwini and Gebru '
    '[20] demonstrated empirically, in commercial vision systems, that '
    'aggregate accuracy can conceal severe subgroup failure - the point this '
    'project transfers to game telemetry. The obstacle is that this literature '
    'almost universally audits protected demographic attributes, and '
    'behavioural game logs contain none. Chapter 3 sets out the substitute '
    'adopted; Chapter 4 is explicit about its limits.',

    'Gap addressed. The churn literature predicts well but explains '
    'directionally little and rarely audits subgroup performance; the fairness '
    'literature audits rigorously but presumes demographic attributes this '
    'domain lacks. This project occupies the intersection: it reproduces an '
    'established prediction benchmark, extends it with signed per-player '
    'explanation interpreted against flow theory, and audits the contextual and '
    'behavioural subgroups game logs genuinely contain.',
]

CH2_TECH = [
    'Language and ecosystem. Python was selected over R and Scala. R has '
    'stronger classical statistical tooling, but the sequence model and the '
    'reference SHAP implementation are Python-native, so R would have forced a '
    'cross-language boundary at the two most complex stages. Scala with Apache '
    'Spark would suit a larger corpus, but eleven million events fit '
    'comfortably in memory once stored columnar, and a cluster runtime\'s '
    'overhead would not have been repaid.',

    'Storage. Apache Parquet was chosen for intermediate artefacts over text '
    'and an embedded database. The event tables are read repeatedly - the '
    'sensitivity analysis alone requires four passes - so parsing cost '
    'dominates with text storage, and Parquet\'s columnar layout lets the '
    'feature stage read only the columns it needs. A relational database was '
    'rejected because the access pattern is a full scan grouped by player, so '
    'index maintenance would buy nothing.',

    'Modelling libraries. Four families span the complexity spectrum rather '
    'than maximising any single score. Penalised logistic regression from '
    'scikit-learn [21] gives an interpretable linear baseline; random forests '
    '[14] a bagged non-linear ensemble robust to feature scaling; XGBoost [15] '
    'regularised gradient boosting - the family that won two of three games in '
    'the source study, and therefore the key comparator. A long short-term '
    'memory network [16] in PyTorch [22] operates on daily behaviour vectors '
    'rather than aggregated features, testing whether temporal ordering carries '
    'signal aggregation destroys. PyTorch was preferred to TensorFlow for its '
    'define-by-run execution, which eased debugging of sequence batching.',

    'Explainability tooling. The reference SHAP library was selected over LIME '
    'and permutation importance. The latter yields unsigned global rankings '
    'only, and this project\'s central finding depends on sign; LIME gives '
    'local explanations without the additivity and consistency guarantees of '
    '[11]. The exact tree algorithm [12] additionally makes ensemble '
    'explanation tractable at cohort scale.',

    'Fairness tooling. Established fairness toolkits were considered and not '
    'adopted. They are built around protected attributes and mitigations that '
    'reweight or post-process predictions per group. This project has no '
    'protected attributes, and per-group post-processing is precisely what the '
    'audit design rejects, since scoring each subgroup at its own threshold '
    'would conceal the disparity being measured. The audit was implemented '
    'directly at a single shared threshold.',

    'Decompression. The Deflate64 defect described in Chapter 3 forced a '
    'specific technology decision. The conventional remedy is the '
    'zipfile-deflate64 package, which could not be installed in the project '
    'environment because it requires a C compiler that was unavailable. A '
    'dependency on an external 7-Zip binary was rejected as it would have made '
    'the pipeline non-reproducible on a clean machine. The pure-Python '
    'inflate64 package was selected instead and wrapped in a custom streaming '
    'reader.',
]

CH2_SUMMARY = [
    'The literature establishes that churn is predictable from generic '
    'behavioural features, that the label must be constructed with explicit and '
    'testable parameters, and that timing and censoring are real threats to '
    'validity. It also establishes two capabilities the game churn literature '
    'has under-used: signed per-player attribution, which turns a prediction '
    'into a design insight, and subgroup auditing, which turns an aggregate '
    'score into a distributional claim. The weakness running through the '
    'reviewed work is over-reliance on aggregate performance figures; Rudin\'s '
    'critique of post-hoc explanation [13] and Buolamwini and Gebru\'s '
    'demonstration of concealed subgroup failure [20] point at that same blind '
    'spot from different directions.',

    'The technology review favours a single-machine Python pipeline with '
    'columnar storage, four heterogeneous model families, and Shapley '
    'explanation applied to both a linear and a tree model. Its strengths are '
    'reproducibility, low overhead and direct access to the required '
    'explanation tooling; its weakness is that it would not scale to a much '
    'larger corpus without a distributed runtime, accepted here because the '
    'analysis is offline and the corpus fixed.',
]

# ------------------------------------------------------------- chapter 3 ----

CH3_IMPL = [
    'This chapter describes how the methodology was realised. It begins with '
    'the pipeline architecture, then treats in detail the two archive defects '
    'that had to be solved before any analysis was possible, and continues '
    'through labelling, feature engineering, modelling, explanation and audit.',

    '3.1 Pipeline Architecture',

    'The system is organised as nine source modules under a single package, '
    'each owning one stage and each writing a durable artefact. Configuration - '
    'paths, window parameters and random seeds - is centralised in a single '
    'module so that no stage carries its own hard-coded constants. A headless '
    'runner executes the whole sequence for reproducibility, and seven '
    'notebooks reproduce the same stages with narrative and inline figures for '
    'examination. All random seeds are fixed, and the split between training '
    'and evaluation is stratified by the churn label so that the class balance '
    'is preserved on both sides.',

    'The staged design earned its cost during development. Because the '
    'extraction artefacts persist, the four-configuration sensitivity analysis '
    'in Chapter 4 re-runs only labelling, feature engineering and modelling, '
    'reducing what would have been a repeated multi-minute extraction to a '
    'single pass.',

    '3.2 Extraction and the First Difficult Problem: Deflate64',

    'The raw data is published as one comma-separated file and two multi-part '
    'ZIP archives totalling approximately 853 megabytes [2]. Extraction of the '
    'second game failed immediately. Seven of its eight archive parts are '
    'compressed with method 9, Deflate64 - an Enhanced Deflate variant that '
    'raises the sliding window from 32 kilobytes to 64 kilobytes - and the '
    'Python standard library\'s zipfile module raises NotImplementedError when '
    'it encounters this method. The failure affects seven eighths of the '
    'largest game in the study, so it could not be worked around by exclusion.',

    'Three remedies were evaluated. The zipfile-deflate64 package is the '
    'conventional answer but requires compilation of a C extension, and no C '
    'compiler was available in the project environment; installation failed. '
    'Shelling out to an external 7-Zip executable would have worked on the '
    'development machine but would have introduced an undeclared system '
    'dependency, breaking reproducibility on any clean environment - '
    'unacceptable for a submitted artefact. Full decompression to a temporary '
    'directory was rejected on memory and disk grounds.',

    'The adopted solution, implemented in a dedicated reader module, bypasses '
    'the standard library\'s member-reading path entirely. The reader parses '
    'the archive\'s central directory itself to locate each member\'s local '
    'header, seeks to the start of the raw compressed byte range, and streams '
    'that range in fixed-size chunks into a pure-Python inflate64 decompressor, '
    'yielding decoded output incrementally. Because the design never '
    'materialises a whole member, memory consumption stays flat and independent '
    'of archive size, and because inflate64 is pure Python the pipeline '
    'installs from the requirements file alone on any machine with a supported '
    'interpreter. The trade-off accepted is throughput: pure-Python inflation '
    'is slower than a compiled implementation, but at roughly four minutes for '
    'the full extraction across all three games this cost is immaterial for an '
    'offline pipeline that runs once.',

    '3.3 The Second Difficult Problem: A Structurally Truncated JSON File',

    'The third game presented a subtler defect. Its player file is delivered at '
    'its full declared size of 933,730,335 bytes, so no size check or checksum '
    'against the manifest reveals a problem, and the file opens without '
    'complaint. However, the JSON is structurally incomplete: the byte stream '
    'ends with a closing bracket for the inner array but never closes the outer '
    'object. Strict parsers therefore consume roughly 411,000 of approximately '
    '713,000 records before aborting with an unexpected end-of-input error, '
    'silently discarding more than 40% of the game\'s players.',

    'Diagnosis was the harder half of this problem. Because the file is the '
    'correct size and the early records parse cleanly, the initial symptom was '
    'an unexplained parse failure deep into a nine-hundred-megabyte file rather '
    'than an obvious corruption. Byte-level inspection of the file tail '
    'confirmed the missing closing brace.',

    'The repair is deliberately minimal. A thin stream wrapper interposes '
    'between the file object and the incremental JSON parser, passing every '
    'read straight through until genuine end-of-file is reached, at which point '
    'it emits the single missing brace character exactly once and then reports '
    'end-of-file normally. No record content is synthesised, altered or '
    'inferred; the repair supplies one structural delimiter and nothing else. '
    'This distinction was treated as a matter of research integrity rather than '
    'engineering convenience - fabricating records to fill a gap would '
    'invalidate every downstream number.',

    'One non-obvious defect emerged during implementation. The incremental '
    'parser issues a zero-length read as a probe before beginning to consume '
    'the stream. A first implementation treated any read returning no bytes as '
    'end-of-file, which caused the one-shot repair to fire on that probe, '
    'inserting the brace at the very start of the stream and corrupting the '
    'parse immediately. The wrapper therefore distinguishes an explicit '
    'zero-length request from a genuine exhausted read, and only the latter '
    'triggers the repair. This is recorded because the failure was silent '
    'rather than loud, and because it illustrates that a defensive repair can '
    'itself introduce a defect if the interface it wraps is not fully '
    'understood.',

    '3.4 Extraction Validation',

    'Because both problems above required custom readers, the extraction '
    'demanded external validation - a self-consistent pipeline can be '
    'consistently wrong. The independently extracted totals were compared '
    'against the counts published by Kim et al. [1].',

    '[[TAB:etl_check|Independently extracted totals compared against the counts published in the source study]]',

    'The extraction recovers slightly more than the published totals, within '
    '4% on records and under 2% on players. A modest excess is the expected '
    'direction: the published study applied filtering steps before reporting, '
    'whereas these figures are taken at the tidy-event stage prior to cohort '
    'construction. Agreement at this level across three independently processed '
    'archives, two of which required custom readers, provides reasonable '
    'assurance that neither reader silently dropped or duplicated data.',

    '[[TAB:datasets|The three commercial games analysed, as extracted]]',

    '3.5 Churn Labelling and Censoring Guards',

    'Churn is defined following [1] using two windows. The observation period '
    'comprises the first n days following a player\'s first ever recorded '
    'session, and all features are computed strictly within it. The churn '
    'prediction period comprises the following m days; a player recording zero '
    'sessions throughout it is labelled a churner. Defaults of five and ten '
    'days respectively follow the source study, with alternatives evaluated in '
    'Chapter 4.',

    'This definition was extended with two censoring guards that the source '
    'study leaves implicit. The right guard requires the full observation and '
    'prediction window to fall inside the observed log. Without it, players '
    'whose window extends past the end of logging are labelled churners purely '
    'because the data stops, and the model partly learns to detect the end of '
    'the recording period rather than departure - a leak that inflates measured '
    'performance while producing a model that cannot work in deployment, where '
    'the log always ends today. The left guard excludes players first seen in '
    'the opening days of the log, since such players may have been active '
    'before logging began and are therefore not genuinely new; their apparent '
    'first session is an artefact of when recording started.',

    'Both guards shrink the usable cohort - the first game falls from 25,956 '
    'observed players to a 25,121-player cohort - and both were adopted despite '
    'this cost because each removes label noise that would otherwise flatter '
    'the results. This is a deliberate trade of measured performance for '
    'validity.',

    'Leakage control is enforced at the feature layer rather than by '
    'convention. Every feature function receives only events timestamped before '
    'the observation period ends, so no quantity derived from the label window '
    'can reach the model even by accident.',

    '[[TAB:cohorts|Labelled cohorts under the default five-day observation and ten-day prediction windows]]',

    'The cohorts differ sharply in character. The first game is extreme, with '
    '92.6% churn and a median of two events per player in the observation '
    'window; the second is denser at 31 median events; the third is the most '
    'balanced at 60.0% churn. These differences matter for interpretation, and '
    'Chapter 4 argues that they explain much of the cross-game variation in '
    'measured performance.',

    '[[FIG:game2_cohort_overview.png|Cohort composition and behavioural distributions for the racing game]]',

    '3.6 Feature Engineering',

    'Features are computed per player within the observation period and fall '
    'into five groups. Volume features count sessions, plays, active days and '
    'total playtime. Temporal features capture the rhythm of engagement - mean, '
    'maximum and standard deviation of inter-session gaps, recency of the last '
    'event, active duration, and the ratio of consecutive active days - '
    'following the generic-feature argument of [3]. Distributional features '
    'record when play occurs, including night and weekend ratios and the spread '
    'of active hours. Outcome features, available where a game exposes them, '
    'cover scores, win and fail ratios, completion and quit ratios, and streak '
    'lengths. Monetisation features, available for the racing game only, cover '
    'purchase counts, totals and first-purchase timing. A per-day breakdown of '
    'activity across the five observation days is also produced, giving the '
    'tabular models limited access to trajectory.',

    'The feature set is intentionally wider than any single game requires; '
    'features not derivable from a given game\'s events are simply absent for '
    'that game, and the modelling stage adapts to the available columns. This '
    'avoids maintaining three divergent feature pipelines.',

    '3.7 Modelling',

    'Four model families were trained per game. Logistic regression uses L2 '
    'penalisation with standardised inputs and class weighting to counter the '
    'imbalance. The random forest [14] and XGBoost [15] models use fixed seeds '
    'and moderate depth limits, with the boosting model additionally given a '
    'scaled positive weight. The sequence model [16] departs from the tabular '
    'representation entirely: rather than consuming aggregated features it '
    'consumes a per-day matrix of behaviour vectors across the observation '
    'window, allowing it in principle to distinguish a player whose activity is '
    'rising from one whose identical total is falling - a distinction that '
    'aggregation destroys. It comprises a single recurrent layer followed by a '
    'dense classification head, trained with early stopping on a held-out '
    'split, and runs on the processor in approximately forty seconds for the '
    'first game.',

    'Evaluation avoids accuracy deliberately. On the first game, predicting '
    'churn for every player yields over 0.90 accuracy while providing no usable '
    'information, and churn-class precision is similarly inflated by the base '
    'rate. Reporting therefore leads with the area under the receiver operating '
    'characteristic curve, the area under the precision-recall curve for the '
    'retained class expressed as lift over that class\'s own base rate, and '
    'balanced accuracy. The retained class is chosen as the positive class '
    'because it corresponds to the actionable business question - which players '
    'will stay - and because it is the minority class, where performance is '
    'genuinely difficult.',

    '3.8 Explainability',

    'Shapley additive explanations [11] were computed for the penalised linear '
    'model and, on the first game, for the boosted tree model using the exact '
    'tree algorithm [12]. Four artefacts are produced per model: a beeswarm '
    'plot showing the distribution of signed attributions per feature, a bar '
    'chart of mean absolute attribution, dependence plots for the highest-'
    'ranked features, and waterfall plots decomposing the single '
    'highest-risk and single lowest-risk prediction in the cohort.',

    'A signed summary is also written to disk, recording for each feature both '
    'its mean absolute attribution and the direction in which it predominantly '
    'pushes predictions. This artefact carries the finding reported in Chapter '
    '4; an unsigned importance ranking of the kind reported in the source study '
    'would have concealed it entirely.',

    '3.9 Fairness Audit',

    'The audit had to be designed around a hard constraint: the logs contain no '
    'protected demographic attributes whatsoever - no age, gender, ethnicity, '
    'income or location. A conventional demographic audit of the kind '
    'formalised in [18] and surveyed in [19] is therefore impossible on this '
    'data. Rather than substitute a proxy and present it as demography, which '
    'would be misleading, the project states the limitation plainly and audits '
    'the attributes that genuinely exist.',

    'Two categories were used. Contextual attributes are recorded directly in '
    'the logs: platform and device family for the racing game. Behavioural '
    'segments are derived by tercile split within each game: engagement tier '
    'from observation-period activity volume, skill tier from outcome '
    'performance, and spend tier from purchase behaviour where available.',

    'One design decision governs the whole audit. All subgroups are scored at a '
    'single shared decision threshold rather than at per-group optimised '
    'thresholds. Per-group thresholds would improve every group\'s apparent '
    'error rates and would conceal exactly the disparity the audit exists to '
    'measure; they also correspond to a deployment practice - treating players '
    'differently by segment - that would require separate justification. For '
    'each subgroup the audit records the area under the receiver operating '
    'characteristic curve, false negative and false positive rates, and '
    'selection rate, and reports the gap between best and worst served group '
    'per attribute.',
]

# ------------------------------------------------------------- chapter 4 ----

CH4_EVAL = [
    'This chapter evaluates the system against the objectives of Chapter 1: '
    'model performance across the three games, Shapley interpretation, the '
    'fairness audit, robustness to the labelling parameters, and the strengths '
    'and weaknesses of the outcome.',

    '4.1 Model Performance',

    'All four model families were trained and evaluated on all three games.',

    '[[TAB:results|Model performance across all three games, ordered by area under the receiver operating characteristic curve within each game]]',

    '[[FIG:cross_game_summary.png|Cross-game comparison of model performance]]',

    'Three observations follow. First, there is no universal winner. The '
    'sequence model leads on the first game at 0.7834, penalised logistic '
    'regression on the second at 0.7585 and the third at 0.8056. This '
    'reproduces the central methodological conclusion of [1] - that the '
    'appropriate architecture is game-specific and cannot be lifted from a '
    'published result - from an independent implementation, which strengthens '
    'rather than merely repeats the claim.',

    'The replication is nonetheless partial and is reported as such. Kim et al. '
    '[1] found the sequence model best on their first game and gradient '
    'boosting best on the other two. This project agrees on the first game but '
    'finds logistic regression rather than gradient boosting ahead on the '
    'remaining two. The disagreement is small - on the second game logistic '
    'regression leads XGBoost by 0.0003 area under curve, well inside any '
    'meaningful difference - and the source study itself observes that '
    'inter-algorithm differences were minimal. The honest reading is that the '
    'ordering among top models on those games is not stable enough to support a '
    'claim either way, and that the reproducible finding is the absence of a '
    'universal winner rather than the identity of one.',

    'Second, the simple linear model is competitive everywhere. On the third '
    'game the spread across all four families is 0.0023 area under curve. Where '
    'behavioural signal is strong and largely monotonic, additional complexity '
    'buys almost nothing. This negative result is reported as a substantive '
    'finding rather than a disappointment: it argues directly for deploying the '
    'interpretable model, and converges with Rudin\'s contention [13] that the '
    'presumed accuracy cost of interpretability is often illusory. The linear '
    'model also trains in 0.2 seconds against 33 for the random forest on the '
    'second game, which matters under frequent retraining.',

    'Third, the sequence model\'s advantage appears only where trajectory '
    'carries information aggregation destroys. Its clearest win is the first '
    'game, the sparsest cohort, where per-day ordering is nearly all the signal '
    'available; on the denser second game it places last. The architecture is '
    'not generically superior but suited to short, sparse traces.',

    '[[FIG:game1_model_curves.png|Receiver operating characteristic, precision-recall and calibration curves for the first game]]',

    '4.2 Why Accuracy Is Not Reported',

    'The cohorts are heavily churn-dominated, at 92.6%, 75.5% and 60.0%. On the '
    'first game a constant predictor answering "churn" for everyone achieves '
    'over 0.90 accuracy while carrying no information, and the same degeneracy '
    'inflates churn-class F1 - which reaches 0.964 for logistic regression '
    'there while the retained-class F1 is 0.186. Reporting the former without '
    'the latter would be actively misleading.',

    'The evaluation therefore leads with retained-class precision-recall '
    'performance measured against that class\'s own base rate, following Saito '
    'and Rehmsmeier [17]. The first game\'s sequence model achieves 0.3538 '
    'against a 0.0740 base rate - a lift of 4.78 times. Absolute '
    'precision-recall values are not comparable across games because the base '
    'rates differ fivefold; lift is. This yields a counter-intuitive result '
    'worth stating: the first game has by far the worst absolute retained-class '
    'performance yet by far the best lift, because retained players are so rare '
    'there that identifying them at all is a substantial achievement.',

    '4.3 What Drives Churn: Shapley Interpretation',

    'Shapley attribution turns the models from predictors into design '
    'instruments. On the first game the strongest protective signal is mean '
    'score, followed by session count and maximum inter-session gap, with '
    'higher scores and more sessions pushing predictions towards retention. '
    'This is intuitive and consistent with the generic-feature account of [3].',

    'The second game produces the project\'s principal interpretive finding.',

    '[[TAB:shap_game2|Highest-attribution features for the racing game, with the direction in which each pushes predictions]]',

    '[[FIG:game2_logistic_regression_shap_beeswarm.png|Signed Shapley attributions for the racing game, showing the direction and distribution of each feature\'s contribution]]',

    'Win ratio is the single highest-attribution feature, and it pushes '
    'predictions towards churn; attempt count and completion ratio protect '
    'retention. The plain reading is that players who win too easily leave. '
    'Fail ratio and quit ratio also push towards churn, so this is not a simple '
    'monotone preference for difficulty: both excessive success and excessive '
    'failure are associated with departure, while sustained engaged attempting '
    'is associated with staying.',

    '[[FIG:game2_logistic_regression_shap_dependence_win_ratio.png|Dependence of the win-ratio attribution on the win-ratio value for the racing game]]',

    'This is the flow channel of Csikszentmihalyi [8] appearing directly in '
    'commercial telemetry, and its operational form in the GameFlow model of '
    'Sweetser and Wyeth [9]. It is equally consistent with the '
    'self-determination account of Ryan et al. [10]: a player who wins without '
    'effort receives no evidence of competence, and that need goes unsatisfied '
    'precisely because success is guaranteed. It also converges independently '
    'on the premise of Li et al. [6], recovering the same mechanism from '
    'explanation of a model given no difficulty structure - arguably stronger '
    'evidence that the effect lies in the data rather than in the modelling '
    'assumptions.',

    'The methodological point is that this finding is unreachable without '
    'signed per-player attribution. An unsigned importance ranking of the kind '
    'reported in the source study would place win ratio at the top and stop '
    'there, leaving the natural assumption - that winning aids retention - '
    'unchallenged. The direction is the finding.',

    'Two cautions apply. Shapley values explain the model, not the game: they '
    'establish that the model relies on win ratio in this direction, which is '
    'evidence about the data but not proof of a mechanism. And because the logs '
    'record no intervention, nothing here shows that adjusting difficulty would '
    'retain a player; that requires a controlled experiment, proposed as future '
    'work.',

    '4.4 Fairness Audit',

    'The audit\'s first result is a negative one that must be stated before any '
    'other: the logs contain no protected demographic attributes, so the '
    'demographic fairness question posed in the original proposal cannot be '
    'answered with this data. No demographic claim is made anywhere in this '
    'report; what follows audits contextual and behavioural attributes only.',

    '[[TAB:fairness|Subgroup performance disparities, all groups scored at a single shared threshold]]',

    '[[FIG:game1_fairness.png|Subgroup performance for the first game]]',

    'The headline result concerns engagement tier, and it replicates. On the '
    'first game the gap between best- and worst-served engagement tier is '
    '0.250 area under curve; on the third game it is 0.242. These are two '
    'independent games with different genres, platforms and cohort '
    'compositions, producing near-identical disparities. On the first game the '
    'model is barely distinguishable from a coin flip for light players at '
    '0.521 while performing strongly for heavy players at 0.771.',

    'The consequence is the ethical core of the project. The retention system '
    'works worst for exactly the casual majority most at risk of leaving and '
    'cheapest to retain, and best for the committed players least likely to '
    'leave anyway. A studio allocating intervention budget by model score would '
    'systematically under-serve the group with most to gain, and because those '
    'interventions shape the experience players subsequently receive, the '
    'disparity would compound rather than remain static. This is a concrete '
    'instance of a machine-learning system amplifying an existing engagement '
    'gradient, and it is precisely the failure mode Buolamwini and Gebru [20] '
    'demonstrated in another domain: aggregate performance of 0.78 on the first '
    'game conceals near-random performance for a large subgroup.',

    'A mechanical explanation exists and does not diminish the finding. Light '
    'players generate very little behavioural evidence, so less signal '
    'separates the departing from the returning. That this is a cold-start '
    'problem rather than deliberate bias explains the disparity but does not '
    'remove its consequences; the response is to report performance per segment '
    'and treat low-engagement prediction as unsolved rather than averaged '
    'away.',

    'The audit also produced a clean negative result. On the racing game the '
    'platform gap is negligible at 0.006, iOS 0.761 against Android 0.755. '
    'Reporting a null finding honestly strengthens the credibility of the '
    'disparities that were found; an audit finding problems everywhere it '
    'looked would invite the suspicion that its method manufactures them.',

    'Skill tier requires caution. The worst-served group is high-skill players '
    'on the racing game but low-skill players on the third, so the direction '
    'does not replicate and no universal skill effect is claimed. Only the '
    'engagement-tier disparity replicates, and it is the only subgroup finding '
    'advanced with confidence.',

    '4.5 Robustness to the Labelling Windows',

    'Because the churn label is constructed rather than observed, the stability '
    'of the conclusions under different window choices is a genuine threat to '
    'validity. The full pipeline was re-run on the racing game under four '
    'configurations.',

    '[[TAB:sensitivity|Sensitivity of the racing game to the observation and churn prediction window parameters]]',

    '[[FIG:game2_window_sensitivity.png|Effect of the observation and prediction windows on labelled churn rate and model performance]]',

    'The labelled churn rate moves substantially, from 70.2% to 78.3%, while '
    'the area under the receiver operating characteristic curve stays within a '
    'band of 0.0151, from 0.7417 to 0.7581. The model is therefore detecting '
    'behavioural signal that persists regardless of where the boundary falls, '
    'not an artefact of one labelling choice. This is the strongest single '
    'piece of evidence for the approach\'s validity, and is available only '
    'because the label was parameterised rather than fixed - a direct '
    'inheritance from [1].',

    'Retained-class precision-recall performance is more sensitive, from 0.5542 '
    'to 0.6248, but this is expected: that metric is measured against a base '
    'rate which moves with the churn rate by construction.',

    '4.6 Strengths and Weaknesses',

    'Four strengths stand out. The extraction is externally validated against '
    'published counts rather than merely self-consistent. The label is '
    'parameterised and its influence measured rather than assumed. The '
    'interpretation is signed and per-player, producing a finding aggregate '
    'importance could not. And the evaluation is distributional, producing a '
    'finding aggregate performance concealed.',

    'The weaknesses are equally clear and are not mitigated by the above. The '
    'labels are proxies: churn is inferred from inactivity, so a player '
    'returning one day after the window closes is recorded as a churner, and no '
    'modelling sophistication corrects a noisy target. Absolute performance is '
    'moderate - 0.74 to 0.81 area under curve - useful for ranking but '
    'insufficient for automated individual decisions, and near-useless for '
    'low-engagement players on one game. The Shapley interpretation establishes '
    'association, not causation. And because no intervention was applied in '
    'these logs, the project cannot show that acting on its predictions would '
    'retain anyone.',

    'Weighed together, the artefact succeeds as a ranking and diagnostic '
    'instrument and fails as an automated decision system - and the evaluation '
    'was designed to make that distinction visible rather than hide it behind a '
    'headline figure.',
]

CH4_RELATED = [
    'The most direct comparator is Kim et al. [1], whose data and churn '
    'definition this project adopts. This project reproduces their sequence-'
    'model result on the first game and diverges on the other two, where '
    'penalised logistic regression edges ahead by margins too small to be '
    'meaningful; their conclusion that no single architecture dominates is '
    'reproduced. The work is extended in three respects: explicit censoring '
    'guards, signed Shapley attribution in place of unsigned feature '
    'importance, and a subgroup fairness audit their study does not attempt.',

    'Hadiji et al. [3] argued for generic, transferable behavioural features. '
    'The results support that position with a qualification: generic temporal '
    'features carry most of the signal on the sparse first game, but the '
    'strongest single attribution on the racing game is an outcome feature, win '
    'ratio, which is not transferable in their sense. Generic features appear '
    'sufficient for prediction and insufficient for explanation.',

    'Runge et al. [4] evaluated churn models by campaign impact on high-value '
    'players. Their business-impact framing motivates the lift-based reporting '
    'used here, but their restriction to high-value players is the practice '
    'this project\'s audit calls into question: such filtering would exclude '
    'precisely the low-engagement segment where the model demonstrably '
    'underperforms, rendering a known weakness invisible.',

    'Li et al. [6] built difficulty-awareness into a churn framework by design '
    'and demonstrated intervention benefit. This work reaches a compatible '
    'conclusion by a different route. Their study is stronger on intervention, '
    'having tested it; this one is stronger on independence of evidence, having '
    'not assumed the mechanism it found.',

    'Bertens et al. [5] and Viljanen et al. [7] model churn timing through '
    'survival analysis rather than binary classification, a framing better '
    'suited to the phenomenon since departure is a time-to-event process. The '
    'binary framing was retained for comparability with [1]; Chapter 5 '
    'identifies the survival approach as the most promising extension.',

    'Relative to the fairness literature [18], [19], [20], this project is '
    'necessarily partial: it audits behavioural and contextual subgroups '
    'because protected attributes are absent, and cannot speak to demographic '
    'fairness. It contributes the observation that behavioural subgroup '
    'auditing is worth performing in its own right, since the engagement-tier '
    'disparity found here is large, replicated across two games, and directly '
    'consequential for intervention budget.',
]

# ------------------------------------------------------------- chapter 5 ----

CH5_CONC = [
    'This project set out to predict player churn from behavioural telemetry, '
    'to explain which in-game systems drive it, and to test whether the '
    'resulting model serves all players equally. All six objectives were met.',

    'A reproducible pipeline was built that extracts 11,290,849 events for '
    '196,486 players from three commercial games, validated externally against '
    'the counts published in the source study to within 4%. Two genuine defects '
    'in the published archives were diagnosed and solved without introducing '
    'system dependencies or fabricating data: a Deflate64 compression method '
    'the Python standard library cannot read, and a structurally truncated JSON '
    'file delivered at its full declared size. A parameterised churn label was '
    'implemented and strengthened with two censoring guards, and four model '
    'families were compared under metrics appropriate to a severely imbalanced '
    'target.',

    'The predictive conclusion is that churn is detectable but not sharply so, '
    'at between 0.74 and 0.81 area under the receiver operating characteristic '
    'curve, and that no architecture wins universally. A penalised linear model '
    'is competitive on all three games and best on two, with a spread across '
    'all four families of 0.0023 on one game. Model complexity is not what '
    'limits performance here; label quality and behavioural sparsity are.',

    'The interpretive conclusion is that on the racing game a high win ratio '
    'pushes predictions towards churn while sustained attempting and completion '
    'protect retention. Difficulty that is too low is a retention risk in the '
    'same way that difficulty that is too high is - the flow channel, visible '
    'in commercial telemetry rather than in self-report. This is directly '
    'actionable for design in a way that a churn probability is not, and it is '
    'reachable only through signed per-player attribution.',

    'The equity conclusion is the most consequential. The model performs '
    'markedly worse for low-engagement players, with a disparity of 0.250 on '
    'the first game and 0.242 on the third - two independent games, near '
    'identical magnitude, which makes it a finding rather than an artefact. On '
    'the first game performance for light players is barely better than chance. '
    'A retention system built on this model would serve the casual majority '
    'worst while serving committed players best, and since such systems shape '
    'the experience players subsequently receive, the gap would widen rather '
    'than close. The demographic fairness question posed in the original '
    'proposal could not be answered, because the logs contain no protected '
    'attributes; stating that plainly, rather than substituting a proxy and '
    'implying otherwise, is treated here as part of the contribution.',

    'The overall outcome is an artefact that functions well as a ranking and '
    'diagnostic instrument for design teams and poorly as an automated '
    'individual decision system - and an evaluation designed to make that '
    'distinction visible rather than to conceal it.',
]

CH5_FUTURE = [
    'Survival modelling. The clearest methodological extension is to replace '
    'the binary label with a time-to-event formulation following [5] and [7]. '
    'This would predict when a player will leave rather than whether, would '
    'handle censoring natively rather than through the guards added here, and '
    'would remove the sensitivity to window placement documented in Chapter 4.',

    'Controlled intervention. The most valuable extension is also the one this '
    'data cannot support. Nothing in an observational log demonstrates that '
    'acting on a prediction changes an outcome. A controlled experiment, in '
    'which matched at-risk players receive a difficulty adjustment or an '
    'incentive and outcomes are compared against a held-out control, is the '
    'only way to convert the win-ratio finding into a validated design '
    'recommendation.',

    'Agent-based simulation of design change. The original proposal included an '
    'agent-based simulation of how design parameter changes propagate to '
    'aggregate retention. This was deliberately scoped out rather than rushed. '
    'Such a simulation requires a validated model of how players respond to '
    'design changes, and that response function cannot be identified from '
    'observational logs in which no design change was ever applied; building it '
    'on the present data would produce a simulation whose behaviour was an '
    'artefact of its own assumptions. It becomes tractable only once '
    'intervention data of the kind described above exists, and it is proposed '
    'as the phase following it rather than as an omission from this one.',

    'Cold-start improvement. Since the largest disparity found is a cold-start '
    'problem, the most useful accuracy work is not a better classifier but '
    'better representation of sparse players - transfer from denser cohorts, '
    'hierarchical pooling across games, or explicit uncertainty estimates so '
    'that a low-confidence prediction for a light player is flagged rather than '
    'acted upon.',

    'Demographic fairness. The demographic question remains open and requires '
    'data this project does not have. A study pairing behavioural telemetry '
    'with consented demographic attributes would be able to answer it; a '
    'synthetic dataset would not, since any demographic pattern recovered from '
    'generated data is a property of the generator rather than of players. A '
    'supplementary study on a synthetic dataset was considered for this reason '
    'and rejected.',
]

CH5_REFLECT = [
    'Planning against uncertainty. The project plan allocated a short sprint to '
    'data extraction on the assumption that published archives open cleanly. '
    'Two independent defects made that sprint the longest in the project. The '
    'lesson taken is that plans should allocate contingency by uncertainty '
    'rather than by apparent size: extraction looked trivial and was not, while '
    'modelling looked demanding and proceeded largely to schedule because '
    'mature libraries did most of the work. The contingency was found by '
    'descoping an optional supplementary study, which in retrospect was the '
    'correct trade.',

    'Verification as a working practice. The most valuable habit formed was '
    'refusing to accept plausible-sounding claims without checking them. Early '
    'in the project an automated tool proposed a dataset that did not exist, '
    'supported by convincing record counts and provenance claims; a single '
    'check of the identifier revealed the fabrication. The same discipline '
    'later caught a misattribution of the source paper to the wrong research '
    'group in the project\'s own working notes, which would have placed an '
    'incorrect citation in this report. Both incidents reinforced that '
    'verification cost is trivial next to the cost of an unverified claim '
    'reaching a submitted document, and every reference in this report was '
    'checked against a live publisher record before inclusion.',

    'Metric choice as a design decision. The most significant technical lesson '
    'was that choosing an evaluation metric is a substantive research decision '
    'rather than a reporting formality. An initial pass reported accuracy and '
    'produced results that looked excellent and meant nothing, since a constant '
    'predictor exceeds 0.90 on the first game. Rebuilding the evaluation around '
    'retained-class lift changed not only the presentation but the conclusions, '
    'and it was this reframing that made the cross-game comparison coherent.',

    'The value of negative results. Two of the project\'s more useful outputs '
    'are findings that nothing interesting happened: the near-identical '
    'performance of all four models on the third game, and the negligible '
    'platform gap on the racing game. Both were initially experienced as '
    'disappointments and both turned out to carry weight - the first as an '
    'argument for interpretable deployment, the second as evidence that the '
    'fairness audit does not simply manufacture disparities. Learning to report '
    'these as results rather than to hunt for something more impressive was a '
    'genuine shift in approach.',

    'What would be done differently. Two things. The fairness audit was built '
    'late, after the modelling was complete, and its central finding - that the '
    'model barely works for light players - would have changed feature '
    'engineering priorities had it been available earlier; subgroup evaluation '
    'should have been part of the evaluation harness from the first model '
    'trained, not a subsequent stage. Second, the notebooks were written after '
    'the source modules rather than alongside them, which meant reconstructing '
    'reasoning that had been clear weeks earlier. Writing the narrative '
    'alongside the code would have cost little and preserved more.',
]

# ----------------------------------------------------------- references -----
# Every entry below was verified against a live publisher record, DOI resolution
# or official proceedings listing before inclusion. IEEE style.

REFERENCES = [
    '[1] S. Kim, D. Choi, E. Lee, and W. Rhee, "Churn prediction of mobile and '
    'online casual games using play log data," PLOS ONE, vol. 12, no. 7, '
    'e0180735, Jul. 2017, doi: 10.1371/journal.pone.0180735.',

    '[2] S. Kim, "Churn prediction (rawdata)," Zenodo, Nov. 2016, '
    'doi: 10.5281/zenodo.166035. [Online]. Available: '
    'https://zenodo.org/record/166035',

    '[3] F. Hadiji, R. Sifa, A. Drachen, C. Thurau, K. Kersting, and '
    'C. Bauckhage, "Predicting player churn in the wild," in Proc. IEEE Conf. '
    'Computational Intelligence and Games (CIG), Dortmund, Germany, Aug. 2014, '
    'pp. 131-139, doi: 10.1109/CIG.2014.6932876.',

    '[4] J. Runge, P. Gao, F. Garcin, and B. Faltings, "Churn prediction for '
    'high-value players in casual social games," in Proc. IEEE Conf. '
    'Computational Intelligence and Games (CIG), Dortmund, Germany, Aug. 2014, '
    'pp. 1-8, doi: 10.1109/CIG.2014.6932875.',

    '[5] P. Bertens, A. Guitart, and A. Perianez, "Games and big data: A '
    'scalable multi-dimensional churn prediction model," in Proc. IEEE Conf. '
    'Computational Intelligence and Games (CIG), New York, NY, USA, Aug. 2017, '
    'pp. 33-36. [Online]. Available: https://arxiv.org/abs/1710.02262',

    '[6] J. Li, H. Lu, C. Wang, W. Ma, M. Zhang, X. Zhao, W. Qi, Y. Liu, and '
    'S. Ma, "A difficulty-aware framework for churn prediction and intervention '
    'in games," in Proc. 27th ACM SIGKDD Conf. Knowledge Discovery and Data '
    'Mining (KDD), Aug. 2021, pp. 943-952, doi: 10.1145/3447548.3467277.',

    '[7] M. Viljanen, A. Airola, J. Heikkonen, and T. Pahikkala, "Playtime '
    'measurement with survival analysis," IEEE Trans. Games, vol. 10, no. 2, '
    'pp. 128-138, Jun. 2018.',

    '[8] M. Csikszentmihalyi, Flow: The Psychology of Optimal Experience. '
    'New York, NY, USA: Harper & Row, 1990.',

    '[9] P. Sweetser and P. Wyeth, "GameFlow: A model for evaluating player '
    'enjoyment in games," ACM Computers in Entertainment, vol. 3, no. 3, '
    'pp. 1-24, Jul. 2005, doi: 10.1145/1077246.1077253.',

    '[10] R. M. Ryan, C. S. Rigby, and A. Przybylski, "The motivational pull of '
    'video games: A self-determination theory approach," Motivation and '
    'Emotion, vol. 30, no. 4, pp. 344-360, Dec. 2006, '
    'doi: 10.1007/s11031-006-9051-8.',

    '[11] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting '
    'model predictions," in Advances in Neural Information Processing Systems '
    '30 (NIPS), Long Beach, CA, USA, Dec. 2017, pp. 4765-4774. [Online]. '
    'Available: https://arxiv.org/abs/1705.07874',

    '[12] S. M. Lundberg, G. Erion, H. Chen, A. DeGrave, J. M. Prutkin, '
    'B. Nair, R. Katz, J. Himmelfarb, N. Bansal, and S.-I. Lee, "From local '
    'explanations to global understanding with explainable AI for trees," '
    'Nature Machine Intelligence, vol. 2, no. 1, pp. 56-67, Jan. 2020, '
    'doi: 10.1038/s42256-019-0138-9.',

    '[13] C. Rudin, "Stop explaining black box machine learning models for high '
    'stakes decisions and use interpretable models instead," Nature Machine '
    'Intelligence, vol. 1, no. 5, pp. 206-215, May 2019, '
    'doi: 10.1038/s42256-019-0048-x.',

    '[14] L. Breiman, "Random forests," Machine Learning, vol. 45, no. 1, '
    'pp. 5-32, Oct. 2001, doi: 10.1023/A:1010933404324.',

    '[15] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," '
    'in Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining '
    '(KDD), San Francisco, CA, USA, Aug. 2016, pp. 785-794, '
    'doi: 10.1145/2939672.2939785.',

    '[16] S. Hochreiter and J. Schmidhuber, "Long short-term memory," Neural '
    'Computation, vol. 9, no. 8, pp. 1735-1780, Nov. 1997, '
    'doi: 10.1162/neco.1997.9.8.1735.',

    '[17] T. Saito and M. Rehmsmeier, "The precision-recall plot is more '
    'informative than the ROC plot when evaluating binary classifiers on '
    'imbalanced datasets," PLOS ONE, vol. 10, no. 3, e0118432, Mar. 2015, '
    'doi: 10.1371/journal.pone.0118432.',

    '[18] M. Hardt, E. Price, and N. Srebro, "Equality of opportunity in '
    'supervised learning," in Advances in Neural Information Processing Systems '
    '29 (NIPS), Barcelona, Spain, Dec. 2016, pp. 3315-3323. [Online]. '
    'Available: https://arxiv.org/abs/1610.02413',

    '[19] N. Mehrabi, F. Morstatter, N. Saxena, K. Lerman, and A. Galstyan, '
    '"A survey on bias and fairness in machine learning," ACM Computing '
    'Surveys, vol. 54, no. 6, pp. 1-35, Jul. 2021, doi: 10.1145/3457607.',

    '[20] J. Buolamwini and T. Gebru, "Gender shades: Intersectional accuracy '
    'disparities in commercial gender classification," in Proc. 1st Conf. '
    'Fairness, Accountability and Transparency, PMLR, vol. 81, New York, NY, '
    'USA, Feb. 2018, pp. 77-91. [Online]. Available: '
    'https://proceedings.mlr.press/v81/buolamwini18a.html',

    '[21] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, '
    'O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg, '
    'J. Vanderplas, A. Passos, D. Cournapeau, M. Brucher, M. Perrot, and '
    'E. Duchesnay, "Scikit-learn: Machine learning in Python," Journal of '
    'Machine Learning Research, vol. 12, pp. 2825-2830, Nov. 2011.',

    '[22] A. Paszke, S. Gross, F. Massa, A. Lerer, J. Bradbury, G. Chanan, '
    'T. Killeen, Z. Lin, N. Gimelshein, L. Antiga, A. Desmaison, A. Kopf, '
    'E. Yang, Z. DeVito, M. Raison, A. Tejani, S. Chilamkurthy, B. Steiner, '
    'L. Fang, J. Bai, and S. Chintala, "PyTorch: An imperative style, '
    'high-performance deep learning library," in Advances in Neural Information '
    'Processing Systems 32 (NeurIPS), Vancouver, BC, Canada, Dec. 2019, '
    'pp. 8024-8035.',
]

# ----------------------------------------------------------- appendices -----

_TODO = ('[TO BE COMPLETED BEFORE SUBMISSION] ')

APPENDICES = {
    'Appendix A: Project Proposal': [
        _TODO + 'Insert the approved project proposal document here. The '
        'proposal was not available in the project working directory at the '
        'time this report was generated and must be added by the author.',
    ],
    'Appendix B: Project Management': [
        _TODO + 'Insert evidence of the project management tool used, for '
        'example a screenshot of the Kanban board showing the six sprints '
        'described in Chapter 1, or an equivalent Gantt chart.',
        'The six sprints were: (1) extraction and archive defect resolution, '
        '(2) churn labelling and censoring guards, (3) feature engineering, '
        '(4) model training and evaluation, (5) Shapley explainability, and '
        '(6) fairness audit and reporting.',
    ],
    'Appendix C: Artefact/Dataset': [
        _TODO + 'Insert the link to the code repository here. The complete '
        'implementation - nine source modules, seven notebooks, a headless '
        'pipeline runner and all generated tables and figures - is to be '
        'published to a public repository and the link recorded here.',
        'The underlying dataset is publicly available and is not '
        'redistributed with the code. It may be obtained from Zenodo at '
        'https://zenodo.org/record/166035 under a Creative Commons Attribution '
        '4.0 licence, comprising rawdata_game1.csv (4.8 MB), rawdata_game2.zip '
        '(303.6 MB) and rawdata_game3.zip (544.7 MB).',
        'Reproduction requires installing the dependencies listed in '
        'requirements.txt, placing the three archives in the data/raw '
        'directory, then running the extraction and pipeline entry points '
        'documented in the repository README.',
    ],
    'Appendix D: Screencast': [
        _TODO + 'Insert the link to the video recording demonstrating the '
        'artefact here. No screencast existed at the time this report was '
        'generated and one must be recorded and linked by the author.',
    ],
}
