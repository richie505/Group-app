package com.appsc.prep.data

/**
 * What read-aloud says for the notes: citations taken out, short forms said in full.
 *
 * Citations are the source tags the notes put after facts: [GK], (CDI), (APP; UPSC notes), (IYB 2026),
 * (LENS Apr 2026), (TH, 7 Sep 2026), (APPSC-G2 2025 key) ... - the same codes as each section's
 * "Sources" list - and the grey "Not in your sources: ..." notes. A bracket that mixes a citation with
 * real content keeps the content.
 *
 * Short forms: words around them decide a few (SC, MP, RE ...), then the list below, then the short forms the
 * notes themselves define ("Fiscal Deficit (FD)"), collected into assets/abbr.json by tools/build_abbreviations.py.
 */
object SpeechText {
    /** Short forms defined in the notes: abbreviation -> meanings (most used first). Set by [Repository]. */
    @Volatile var fromNotes: Map<String, List<String>> = emptyMap()

    /** Notes text with its citations taken out ([GK], (CDI; APP), (TH 20 Apr 2026) ...), for showing. */
    fun withoutCitations(text: String): String = removeCitations(text)
        .replace(Regex("""\s*\[[^\]]*$"""), "")
        .replace(Regex("""\(\s*\)"""), "")
        .replace(Regex("""\s+([,.;:)])"""), "$1")
        .replace(Regex("""\s{2,}"""), " ")
        .trim()

    /** Full form of a short form (built-in list, then the notes' own definitions), for the dictionary. */
    fun expand(abbr: String): String? {
        fun one(a: String) = checked[a]?.let { l -> (l.firstOrNull { it.second.isEmpty() } ?: l.first()).first.takeIf { it != "-" } }
            ?: FULL[a] ?: fromNotes[a]?.first()
        return one(abbr) ?: abbr.removeSuffix("s").takeIf { it != abbr }?.let { one(it) }
    }

    /** (block index, text) for a subsection: the title first (-1), then each paragraph; tables row by row. */
    fun parts(title: String, blocks: List<Block>, book: Int, context: String = ""): List<Pair<Int, String>> = buildList {
        // the whole page decides what its short forms mean (CWC next to "juvenile" or next to "dam")
        val page = title + " " + context + " " + blocks.joinToString(" ") { b ->
            when (b) {
                is TextBlock -> b.runs.joinToString("") { it.text }
                is TableBlock -> (listOf(b.head) + b.rows).joinToString(" ") { r -> r.joinToString(" ") { c -> c.joinToString("") { it.text } } }
            }
        }
        fun speakable(text: String, book: Int) = speakable(text, book, page)
        add(-1 to speakable(title, book))
        blocks.forEachIndexed { i, b ->
            when (b) {
                is TextBlock -> {
                    val text = b.runs.filterNot { it.muted && it.text.trimStart().startsWith("Not in your sources") || it.fullForm }
                        .joinToString("") { it.text }
                    speakable(text, book).takeIf { it.any(Char::isLetterOrDigit) }?.let { add(i to it) }
                }
                is TableBlock -> {
                    // headings once ("Table: Factor, How it changes the family."), then each row's values only:
                    // the first cell, then the rest ("Industrialisation: the family moves from ...; ...")
                    val head = b.head.map { c -> speakable(c.filterNot { it.fullForm }.joinToString("") { it.text }, book) }
                        .filter { it.any(Char::isLetterOrDigit) }
                    if (head.isNotEmpty()) add(i to "Table: " + head.joinToString(", ") + ".")
                    b.rows.forEach { r ->
                        val cells = r.map { cell -> speakable(cell.filterNot { it.fullForm }.joinToString("") { it.text }, book) }
                            .filter { it.any(Char::isLetterOrDigit) }
                        val line = when (cells.size) {
                            0 -> ""
                            1 -> cells[0]
                            else -> cells[0].trimEnd('.', ':') + ": " + cells.drop(1).joinToString("; ")
                        }
                        if (line.isNotBlank()) add(i to line)
                    }
                }
            }
        }
    }

    /** One piece of notes text as it should be spoken. [book] picks the meaning of a few short forms. */
    fun speakable(text: String, book: Int = 0, page: String = ""): String {
        var t = text.replace('\n', ' ')
        t = removeCitations(t)
        t = pairs(t)
        t = dropDefinedAcronyms(t)
        t = symbols(t)
        t = numbered(t)
        t = units(t)
        t = acronyms(t, book, page)
        return t.replace(Regex("""\(\s*\)"""), " ")
            .replace(Regex("""\s+"""), " ")
            .replace(Regex("""\s+([,.;:)])"""), "$1")
            .replace(Regex("""\(\s+"""), "(")
            .replace(Regex("""([,;])\1+"""), "$1")
            .trim()
    }

    // ---------------------------------------------------------------- citations

    /** Source codes used in citations (the Sources lists of the notes). */
    private val CODES = setOf(
        "CDI", "CDX", "APP", "APHQ", "TH", "IYB", "APPCA", "APSES", "ES", "SES", "VIS", "LENS", "LENSD", "CDCA",
        "BUD", "PYQ", "PYQs", "UPSC", "APPSC", "G1", "G2", "GS", "PT365", "CA", "NCERT",
        // other exams' papers cited as "(BPSC 2022 key)"
        "BPSC", "JPSC", "UPPSC", "MPPSC", "RPSC", "UKPSC", "CGPSC", "TNPSC", "KPSC", "OPSC", "HPSC", "HPPSC", "WBPSC",
        "TSPSC", "TGPSC", "MPSC", "GPSC", "APSC", "SSC", "CDS", "CAPF", "NDA", "UPPCS", "RAS", "BPSC-TRE",
    )

    private const val MONTH_RE = "(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*"

    private val MONTHS = setOf(
        "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
        "january", "february", "march", "april", "june", "july", "august", "september", "october", "november", "december",
    )

    /** Words that may follow a code inside a citation: (CDI Block04), (APPSC 2019 key), (IYB 2026 data) ... */
    private val FILLER = setOf(
        "key", "keys", "answer", "answers", "notes", "note", "q&a", "highlights", "prelims", "mains", "paper", "part",
        "data", "list", "survey", "update", "updated", "edition", "official", "and", "&", "/", "-", "pp", "p", "ap",
        "i", "ii", "iii", "iv", "block", "unit", "ch", "chapter", "vol", "table", "box", "fig", "printed", "print",
        "says", "gives", "the", "of", "in", "issue", "monthly", "weekly", "daily", "summary", "explanation",
    )

    private fun isFiller(w: String): Boolean {
        val x = w.lowercase().trim('.', ',', ':')
        return x.isEmpty() || x in FILLER || x in MONTHS || x.matches(Regex("""\d{1,4}(st|nd|rd|th)?([-–/]\d{1,4})?""")) ||
            x.matches(Regex("""block\d+""")) || x.matches(Regex("""q\d""")) || x.matches(Regex("""pp?\.?\d.*"""))
    }

    private fun isCode(w: String) = w.trim('.', ',', ':') in CODES

    /** Codes of coaching notes (not real publications): in running text they are read as "one source". */
    private val NOTE_CODES = setOf("CDI", "CDX", "APP", "APHQ", "APPCA", "LENS", "LENSD", "CDCA", "VIS")
    private val NOTE_CODE = Regex("""\b(CDI|CDX|APP|APHQ|APPCA|LENS|LENSD|CDCA|VIS)\b(?:'s|’s)?(?:\s+(?:notes?|Block\s?\d+|PT365|Polity|$MONTH_RE\b|\d{1,4}(?:-\d{2})?))*""")

    /** A bracketed aside that names a source ("APP wrongly says ...", "TH calls it ...") is about sources, not content. */
    private fun namesSource(piece: String) = piece.split(Regex("""[\s\-/,]+""")).any { it.trim('.', ':', '\'', '’', 's') in NOTE_CODES || it in NOTE_CODES || it.removeSuffix("'s").removeSuffix("’s") in CODES && it.removeSuffix("'s").removeSuffix("’s") != "UPSC" && it.removeSuffix("'s").removeSuffix("’s") != "APPSC" }

    /** A piece of a bracket is a citation when it is a source code plus dates, block or key words. */
    private fun isCitation(piece: String): Boolean {
        val p = piece.trim()
        if (p.isEmpty()) return false
        // "APPSC 2025 key: 'non-autonomous' ..." - a note about an answer key: drop it whole
        val head = p.substringBefore(':')
        val words = head.split(Regex("""[\s\-]+""")).filter { it.isNotBlank() }
        if (words.isEmpty() || !isCode(words[0])) return false
        return words.drop(1).all { isCode(it) || isFiller(it) }
    }

    private fun isDate(piece: String) =
        piece.split(Regex("""[\s\-]+""")).filter { it.isNotBlank() }.let { w -> w.isNotEmpty() && w.all { isFiller(it) } }

    private fun removeCitations(text: String): String {
        // [GK], [GK for year], [CDI], [bank GK] ... are all source markers
        var t = text.replace(Regex("""\[[^\[\]]{1,240}]"""), " ")
        // a coaching source named in full
        t = t.replace(Regex("""\bVision(\s+IAS)?\s+PT365(\s+\d{4})?"""), "one source")
        t = Regex("""\(([^()]{1,200})\)""").replace(t) { m ->
            val inner = m.groupValues[1]
            val pieces = inner.split(Regex("""\s*[;,]\s*"""))
            if (pieces.none { isCitation(it) || namesSource(it) }) return@replace m.value
            val keep = pieces.filterNot { isCitation(it) || isDate(it) || namesSource(it) }
            if (keep.isEmpty()) " " else "(" + keep.joinToString(", ") + ")"
        }
        // "Sources: APP, India Year Book, CDI." is not read
        t = t.replace(Regex("""(^|(?<=[.;]\s))Sources?\s*:[^.]*\.?"""), " ")
        // source names left in running text: "CDX names her X; APP gives Y" -> "one source ...; another source ..."
        val seen = mutableListOf<String>()
        t = NOTE_CODE.replace(t) { m ->
            val code = m.groupValues[1]
            val own = if (Regex("""^\w+(['’]s)""").containsMatchIn(m.value)) "'s" else ""
            if (code !in seen) seen += code
            (if (seen.indexOf(code) == 0) "one source" else "another source") + own
        }
        return t
    }

    /** "Fiscal Deficit (FD)": the short form right after its full form is not read again. */
    private fun dropDefinedAcronyms(text: String): String =
        Regex("""(\b[\w'’-]+(?:\s+[\w'’&-]+){0,7})\s*\(([A-Z][A-Za-z&]{1,9})\)""").replace(text) { m ->
            val before = m.groupValues[1]
            val acro = m.groupValues[2].filter { it.isUpperCase() }
            val initials = before.split(Regex("""[\s-]+""")).filter { it.isNotBlank() && it.lowercase() !in setOf("of", "and", "the", "for", "&", "in", "on") }
                .map { it.first().uppercaseChar() }.joinToString("")
            if (acro.length >= 2 && initials.endsWith(acro)) before else m.value
        }

    // ---------------------------------------------------------------- symbols and numbers

    private fun symbols(text: String): String {
        var t = text
        t = t.replace("→", " to ").replace("←", " from ").replace("⇒", " so ").replace("↔", " and ")
        t = t.replace("≈", " about ").replace("~", " about ").replace("≥", " at least ").replace("≤", " at most ")
        t = t.replace(Regex("""(?<=\s|^)>\s?(?=[\d₹])"""), "more than ").replace(Regex("""(?<=\s|^)<\s?(?=[\d₹])"""), "less than ")
        t = t.replace(" – ", ", ").replace(" — ", ", ").replace("—", ", ").replace("–", " to ")
        t = t.replace(Regex("""(?<=\d)\s?°C\b"""), " degrees Celsius").replace("°", " degrees ")
        t = t.replace(Regex("""(?<=[A-Za-z])/(?=[A-Za-z])"""), " or ")
        t = t.replace(Regex("""\be\.g\.,?""", RegexOption.IGNORE_CASE), "for example")
        t = t.replace(Regex("""\bi\.e\.,?""", RegexOption.IGNORE_CASE), "that is")
        t = t.replace(Regex("""\bviz\.,?"""), "namely")
        t = t.replace(Regex("""\bw\.e\.f\.?"""), "with effect from")
        t = t.replace(Regex("""\bw\.r\.t\.?"""), "with respect to")
        t = t.replace(Regex("""\bu/s\b"""), "under section")
        t = t.replace(Regex("""\bvs\.?(?=\s)"""), "versus")
        t = t.replace(Regex("""\betc\.?"""), "etcetera")
        // emphasis in capitals (FIRST/LAST, NOT, ONLY ...) is read as a word
        t = Regex("""\b(FIRST|LAST|NOT|ONLY|NEVER|ALL|NONE|BOTH|EXCEPT|ALWAYS|NOTE|TRUE|FALSE|CORRECT|INCORRECT|WRONG|RIGHT|AND|OR|BUT|NO|YES|ANY|EVERY|MUST|HIGH|LOW|MED|KEY)\b""")
            .replace(t) { it.value.lowercase() }
        t = t.replace(" & ", " and ").replace(Regex("""(?<=[a-z])&(?=[a-z])"""), " and ")
        return t
    }

    private val ROMAN = mapOf(
        "I" to 1, "II" to 2, "III" to 3, "IV" to 4, "V" to 5, "VI" to 6, "VII" to 7, "VIII" to 8, "IX" to 9,
        "X" to 10, "XI" to 11, "XII" to 12, "XIII" to 13, "XIV" to 14,
    )

    /** Sec 6 -> Section 6, Art. 21 -> Article 21, Group-II -> Group 2, No. 5 -> number 5 ... */
    private fun numbered(text: String): String {
        var t = text
        val n = """(?=\s?[\dIVX(])"""
        t = t.replace(Regex("""\bSecs\.?\s?$n"""), "Sections ").replace(Regex("""\bSec\.?\s?$n"""), "Section ")
        t = t.replace(Regex("""\bArts\.?\s?(?=\d)"""), "Articles ").replace(Regex("""\bArt\.?\s?(?=\d)"""), "Article ")
        t = t.replace(Regex("""\bSch\.?\s?(?=[\dIVX])"""), "Schedule ").replace(Regex("""(?<=\d(st|nd|rd|th))\s?Sch\b\.?"""), " Schedule")
        t = t.replace(Regex("""\bCl\.?\s?(?=[\d(])"""), "Clause ").replace(Regex("""\bPara\.?\s?(?=\d)"""), "Paragraph ")
        t = t.replace(Regex("""\bCh\.\s?(?=\d)"""), "Chapter ").replace(Regex("""\bNos?\.\s?(?=\d)""")) { if (it.value.startsWith("Nos")) "numbers " else "number " }
        t = t.replace(Regex("""\bVol\.\s?(?=\d)"""), "Volume ").replace(Regex("""\bFig\.\s?(?=\d)"""), "Figure ")
        t = t.replace(Regex("""\bc\.\s?(?=\d)"""), "circa ").replace(Regex("""\bca\.\s?(?=\d)"""), "circa ")
        t = t.replace(Regex("""\bb\.\s?(?=\d{3,4})"""), "born ").replace(Regex("""\bd\.\s?(?=\d{3,4})"""), "died ")
        t = t.replace(Regex("""\br\.\s?(?=\d{3,4})"""), "reigned ")
        t = t.replace(Regex("""\bGovt\.?"""), "Government").replace(Regex("""\bDept\.?"""), "Department")
        t = t.replace(Regex("""\bUniv\.?(?=\s)"""), "University").replace(Regex("""\bInst\.(?=\s)"""), "Institute")
        t = t.replace(Regex("""\bDr\.\s?(?=[A-Z])"""), "Doctor ").replace(Regex("""\bProf\.\s?(?=[A-Z])"""), "Professor ")
        t = t.replace(Regex("""\bLtd\.?"""), "Limited").replace(Regex("""\bapprox\.?"""), "approximately")
        t = t.replace(Regex("""\best\.\s?(?=\d)"""), "established ")
        // Group-II, Part III, Schedule VII, Phase I ... -> numbers
        t = Regex("""\b(Group|Part|Schedule|Phase|Paper|Unit|Chapter|Class|Book|Block|Stage|Tier|Plan|Grade|Article|List|Edict)([\s-])(XIV|XIII|XII|XI|X|IX|VIII|VII|VI|V|IV|III|II|I)\b""")
            .replace(t) { "${it.groupValues[1]} ${ROMAN[it.groupValues[3]]}" }
        // FY26 -> financial year 2025-26; Q1 -> quarter 1
        t = Regex("""\bFY\s?(\d{2})\b""").replace(t) { val y = it.groupValues[1].toInt(); "financial year 20${"%02d".format(y - 1)}-$y" }
        t = t.replace(Regex("""\bFY\b"""), "financial year").replace(Regex("""\bQ([1-4])\b"""), "quarter $1")
        return t
    }

    /** Units after numbers and rupee amounts. */
    private fun units(text: String): String {
        var t = text
        t = Regex("""(?:₹|\bRs\.?)\s?([\d,.]+)\s?(lakh crore|crore|lakh|Cr\.?|cr\.?|bn|billion|mn|million|trillion)?""").replace(t) { m ->
            val amount = m.groupValues[1].trimEnd('.', ',')
            val unit = when (m.groupValues[2].lowercase().trimEnd('.')) {
                "cr" -> " crore"; "bn" -> " billion"; "mn" -> " million"; "" -> ""; else -> " " + m.groupValues[2]
            }
            "$amount$unit rupees"
        }
        val after = """(?<=\d)\s?"""
        val u = listOf(
            "sq\\.? ?km" to "square kilometres", "km²" to "square kilometres", "km2" to "square kilometres", "km" to "kilometres",
            "MTPA" to "million tonnes per annum", "MMT" to "million metric tonnes", "LMT" to "lakh metric tonnes",
            "MT" to "million tonnes", "GW" to "gigawatts", "MW" to "megawatts", "kW" to "kilowatts", "kWh" to "kilowatt hours",
            "ha" to "hectares", "kg" to "kilograms", "mm" to "millimetres", "cm" to "centimetres", "ft" to "feet",
            "cr" to "crore", "Cr" to "crore", "bn" to "billion", "mn" to "million",
        )
        for ((short, full) in u) t = t.replace(Regex("""$after$short\.?(?![A-Za-z0-9])"""), " $full")
        return t
    }

    // ---------------------------------------------------------------- acronyms

    /** Short forms said in full (plurals add "s" unless listed). */
    private val FULL = mapOf(
        // places
        "AP" to "Andhra Pradesh", "UP" to "Uttar Pradesh", "TN" to "Tamil Nadu", "HP" to "Himachal Pradesh",
        "J&K" to "Jammu and Kashmir", "A&N" to "Andaman and Nicobar", "WB" to "West Bengal", "NCR" to "National Capital Region",
        "UT" to "Union Territory", "UTs" to "Union Territories", "USA" to "United States of America", "US" to "United States",
        "UK" to "United Kingdom", "UAE" to "United Arab Emirates", "USSR" to "Soviet Union", "EU" to "European Union",
        "NE" to "north-east", "SW" to "south-west", "NW" to "north-west", "HQ" to "headquarters",
        "ASR" to "Alluri Sitharama Raju", "SPSR" to "Sri Potti Sriramulu", "KG" to "Krishna-Godavari",
        "VCIC" to "Visakhapatnam-Chennai Industrial Corridor", "NSTR" to "Nagarjunasagar-Srisailam Tiger Reserve",
        // polity
        "PM" to "Prime Minister", "CM" to "Chief Minister", "CJI" to "Chief Justice of India", "HC" to "High Court",
        "HCs" to "High Courts", "AG" to "Attorney General", "CAG" to "Comptroller and Auditor General",
        "CEC" to "Chief Election Commissioner", "ECI" to "Election Commission of India", "EC" to "Election Commission",
        "ECs" to "Election Commissioners", "VP" to "Vice-President", "GG" to "Governor-General", "MLA" to "Member of the Legislative Assembly",
        "MLAs" to "Members of the Legislative Assembly", "MPs" to "Members of Parliament", "LS" to "Lok Sabha", "RS" to "Rajya Sabha",
        "FC" to "Finance Commission", "SFC" to "State Finance Commission", "SFCs" to "State Finance Commissions",
        "UPSC" to "Union Public Service Commission", "APPSC" to "Andhra Pradesh Public Service Commission",
        "SPSC" to "State Public Service Commission", "IAS" to "Indian Administrative Service", "AIS" to "All India Services",
        "ICS" to "Indian Civil Service", "CBI" to "Central Bureau of Investigation", "CVC" to "Central Vigilance Commission",
        "CIC" to "Central Information Commission", "RTI" to "Right to Information", "NHRC" to "National Human Rights Commission",
        "SHRC" to "State Human Rights Commission", "NCW" to "National Commission for Women",
        "NCSC" to "National Commission for Scheduled Castes", "NCST" to "National Commission for Scheduled Tribes",
        "NCBC" to "National Commission for Backward Classes", "NCM" to "National Commission for Minorities",
        "NCPCR" to "National Commission for Protection of Child Rights", "DPSP" to "Directive Principles of State Policy",
        "DPSPs" to "Directive Principles of State Policy", "FR" to "Fundamental Right", "FRs" to "Fundamental Rights",
        "PIL" to "Public Interest Litigation", "IPC" to "Indian Penal Code", "BNS" to "Bharatiya Nyaya Sanhita",
        "BNSS" to "Bharatiya Nagarik Suraksha Sanhita", "PESA" to "Panchayats Extension to Scheduled Areas",
        "ULB" to "Urban Local Body", "ULBs" to "Urban Local Bodies", "PRI" to "Panchayati Raj Institution",
        "GP" to "Gram Panchayat", "ZP" to "Zilla Parishad", "SEC" to "State Election Commission", "MHA" to "Ministry of Home Affairs",
        "INC" to "Indian National Congress", "AICC" to "All India Congress Committee", "TDP" to "Telugu Desam Party",
        "SRC" to "States Reorganisation Commission", "ARC" to "Administrative Reforms Commission", "SCS" to "Special Category Status",
        "OBC" to "Other Backward Class", "OBCs" to "Other Backward Classes", "EWS" to "Economically Weaker Sections",
        "PVTG" to "Particularly Vulnerable Tribal Group", "BPL" to "below poverty line", "CAA" to "Citizenship Amendment Act",
        "RTE" to "Right to Education", "NEP" to "National Education Policy",
        // economy
        "RBI" to "Reserve Bank of India", "GDP" to "gross domestic product", "GSDP" to "gross state domestic product",
        "GVA" to "gross value added", "GST" to "goods and services tax", "FDI" to "foreign direct investment",
        "FPI" to "foreign portfolio investment", "IMF" to "International Monetary Fund", "ADB" to "Asian Development Bank",
        "WTO" to "World Trade Organization", "MSP" to "minimum support price", "MSME" to "micro, small and medium enterprise",
        "NABARD" to "National Bank for Agriculture and Rural Development", "SEBI" to "Securities and Exchange Board of India",
        "SIDBI" to "Small Industries Development Bank of India", "NBFC" to "non-banking financial company",
        "NBFCs" to "non-banking financial companies", "RRB" to "Regional Rural Bank", "PACS" to "primary agricultural credit societies",
        "CRR" to "cash reserve ratio", "SLR" to "statutory liquidity ratio", "MPC" to "Monetary Policy Committee",
        "UPI" to "Unified Payments Interface", "NPCI" to "National Payments Corporation of India", "RTGS" to "real-time gross settlement",
        "NPA" to "non-performing asset", "IBC" to "Insolvency and Bankruptcy Code",
        "FRBM" to "Fiscal Responsibility and Budget Management", "FD" to "fiscal deficit", "RD" to "revenue deficit",
        "BE" to "Budget Estimates", "FAE" to "First Advance Estimates", "AE" to "Advance Estimates", "FRE" to "First Revised Estimates",
        "CSS" to "centrally sponsored schemes", "DBT" to "direct benefit transfer", "PDS" to "public distribution system",
        "FCI" to "Food Corporation of India", "NFSA" to "National Food Security Act", "PLFS" to "Periodic Labour Force Survey",
        "LFPR" to "labour force participation rate", "WPR" to "worker population ratio", "UR" to "unemployment rate",
        "IIP" to "Index of Industrial Production", "HDI" to "Human Development Index", "MPI" to "Multidimensional Poverty Index",
        "GII" to "Gender Inequality Index", "PCI" to "per capita income", "NSO" to "National Statistics Office",
        "SEZ" to "Special Economic Zone", "PLI" to "production-linked incentive",
        "DPIIT" to "Department for Promotion of Industry and Internal Trade", "PSU" to "public sector undertaking",
        "LIC" to "Life Insurance Corporation", "SBI" to "State Bank of India",
        "IRDAI" to "Insurance Regulatory and Development Authority of India", "FEMA" to "Foreign Exchange Management Act",
        "MRTP" to "Monopolies and Restrictive Trade Practices", "CCI" to "Competition Commission of India",
        "TRAI" to "Telecom Regulatory Authority of India", "SHG" to "self-help group", "NRLM" to "National Rural Livelihoods Mission",
        "MGNREGA" to "Mahatma Gandhi National Rural Employment Guarantee Act", "PMAY" to "Pradhan Mantri Awas Yojana",
        "PMKSY" to "Pradhan Mantri Krishi Sinchayee Yojana", "RKVY" to "Rashtriya Krishi Vikas Yojana",
        "ICDS" to "Integrated Child Development Services", "NFHS" to "National Family Health Survey",
        "IMR" to "infant mortality rate", "MMR" to "maternal mortality ratio", "TFR" to "total fertility rate",
        "SRS" to "Sample Registration System", "SERP" to "Society for Elimination of Rural Poverty",
        "APIIC" to "Andhra Pradesh Industrial Infrastructure Corporation", "APCRDA" to "Andhra Pradesh Capital Region Development Authority",
        "APCNF" to "Andhra Pradesh Community-managed Natural Farming", "EXIM" to "Export-Import", "ES" to "Economic Survey",
        "SES" to "Socio-Economic Survey", "APSES" to "Andhra Pradesh Socio-Economic Survey", "IYB" to "India Year Book",
        "TH" to "The Hindu", "BUD" to "Budget", "GS" to "General Studies", "G1" to "Group 1", "G2" to "Group 2",
        "PYQ" to "previous year question", "CA" to "current affairs",
        // international
        "UN" to "United Nations", "UNGA" to "United Nations General Assembly", "UNSC" to "United Nations Security Council",
        "UNESCO" to "United Nations Educational, Scientific and Cultural Organization",
        "UNDP" to "United Nations Development Programme", "UNEP" to "United Nations Environment Programme",
        "UNFCCC" to "United Nations Framework Convention on Climate Change", "WHO" to "World Health Organization",
        "ILO" to "International Labour Organization", "FAO" to "Food and Agriculture Organization",
        "WMO" to "World Meteorological Organization", "IUCN" to "International Union for Conservation of Nature",
        "SCO" to "Shanghai Cooperation Organisation", "SAARC" to "South Asian Association for Regional Cooperation",
        "ASEAN" to "Association of Southeast Asian Nations", "GCC" to "Gulf Cooperation Council", "NAM" to "Non-Aligned Movement",
        "ISA" to "International Solar Alliance",
        // environment
        "NP" to "National Park", "NPs" to "National Parks", "WLS" to "Wildlife Sanctuary", "TR" to "Tiger Reserve",
        "ESA" to "eco-sensitive area", "ISFR" to "India State of Forest Report", "FRA" to "Forest Rights Act",
        "WPA" to "Wildlife Protection Act", "EPA" to "Environment Protection Act", "EIA" to "environmental impact assessment",
        "NGT" to "National Green Tribunal", "CPCB" to "Central Pollution Control Board",
        "APPCB" to "Andhra Pradesh Pollution Control Board", "NAPCC" to "National Action Plan on Climate Change",
        "NDC" to "nationally determined contribution", "COP" to "Conference of the Parties", "CBD" to "Convention on Biological Diversity",
        "GHG" to "greenhouse gas", "CFCs" to "chlorofluorocarbons", "IMD" to "India Meteorological Department",
        "NDMA" to "National Disaster Management Authority", "NDRF" to "National Disaster Response Force",
        "APSDMA" to "Andhra Pradesh State Disaster Management Authority", "GM" to "genetically modified",
        // science
        "ISRO" to "Indian Space Research Organisation", "DRDO" to "Defence Research and Development Organisation",
        "CSIR" to "Council of Scientific and Industrial Research", "ICMR" to "Indian Council of Medical Research",
        "ICAR" to "Indian Council of Agricultural Research", "BARC" to "Bhabha Atomic Research Centre",
        "DAE" to "Department of Atomic Energy", "DST" to "Department of Science and Technology",
        "PSLV" to "Polar Satellite Launch Vehicle", "GSLV" to "Geosynchronous Satellite Launch Vehicle",
        "SSLV" to "Small Satellite Launch Vehicle", "EOS" to "Earth Observation Satellite", "NRSC" to "National Remote Sensing Centre",
        "GPS" to "Global Positioning System", "GIS" to "geographic information system", "AI" to "artificial intelligence",
        "IT" to "information technology", "R&D" to "research and development", "S&T" to "science and technology",
        "EV" to "electric vehicle", "PHWR" to "pressurised heavy water reactor", "BESS" to "battery energy storage system",
        "MNRE" to "Ministry of New and Renewable Energy", "BEE" to "Bureau of Energy Efficiency", "CEA" to "Central Electricity Authority",
        "GI" to "Geographical Indication", "IPR" to "intellectual property rights", "SDG" to "Sustainable Development Goal",
        "AIIMS" to "All India Institute of Medical Sciences", "IIT" to "Indian Institute of Technology",
        "NCERT" to "National Council of Educational Research and Training", "PHC" to "primary health centre",
        "NGO" to "non-governmental organisation", "KPI" to "key performance indicator", "CEO" to "chief executive officer",
        "DG" to "Director General", "LNG" to "liquefied natural gas", "CNG" to "compressed natural gas",
    )

    private fun acronyms(text: String, book: Int, page: String): String {
        val t = text
        val tokens = Regex("""(?<![A-Za-z0-9&-])([A-Z][A-Z0-9&]{0,9}[A-Z0-9])(s?)(?![A-Za-z0-9&]|-[A-Za-z])""")
        return tokens.replace(t) { m ->
            val before = t.substring(0, m.range.first)
            val after = t.substring(m.range.last + 1)
            meaning(m.groupValues[1], m.groupValues[2], before, after, book, page) ?: m.value
        }
    }

    /**
     * Short forms checked against how the notes use them (tools/data/acronyms.tsv -> assets/acronyms.json):
     * short form -> meanings, each with the words that pick it. Set by [Repository].
     */
    @Volatile var checked: Map<String, List<Pair<String, List<String>>>> = emptyMap()

    /**
     * What a short form stands for at this place in the notes ([plural]: "s" for SHGs; [page]: the rest of the
     * page and its titles). Used for both the full form shown on the page and read-aloud.
     * 1. the words around decide a few (SC, MP, RE, CAA ...);
     * 2. the checked list: the meaning whose words appear on the page (CWC: Child Welfare Committee next to
     *    "juvenile", Central Water Commission next to "dam"), else its default; "-" = say it as it is;
     * 3. the built-in list above;
     * 4. a meaning the notes define on another page, only if this page uses its telling words.
     */
    fun meaning(word: String, plural: String, before: String, after: String, book: Int, page: String = ""): String? {
        fun pl(s: String) = if (plural.isNotEmpty()) pluralOf(s) else s
        contextual(word + plural, word, before, after, book)?.let { return it }
        val senses = checked[word + plural]?.let { it to false } ?: checked[word]?.let { it to true }
        if (senses != null) {
            val (list, plural2) = senses
            val near = "$page $before $after"
            // the subject (book) counts double: "CWC" in History is the Congress Working Committee
            fun score(words: List<String>): Int {
                var n = 0
                for (k in words) if (keywordIn(k, near, book)) n += if (k.startsWith("@")) 2 else 1
                return n
            }
            var best: Pair<String, List<String>>? = null
            var bestScore = 0
            for (sense in list) {
                if (sense.second.isEmpty()) continue
                val sc = score(sense.second)
                if (sc > bestScore) { best = sense; bestScore = sc }
            }
            val chosen = best
                ?: list.firstOrNull { it.second.isEmpty() }
                ?: return null
            if (chosen.first == "-") return null
            return if (plural2) pl(chosen.first) else chosen.first
        }
        (FULL[word + plural] ?: FULL[word]?.let(::pl))?.let { return it }
        val notes = fromNotes
        val fromPage = notes[word + plural]?.first() ?: notes[word]?.first()?.let(::pl) ?: return null
        return fromPage.takeIf { fits(it, "$page $before $after".lowercase()) }
    }

    /** "@2" = in book 2; "UP " / "JJB" (capitals) as written; "juvenil" at the start of a word, any case. */
    private fun keywordIn(k: String, text: String, book: Int): Boolean {
        if (k.startsWith("@")) return k.drop(1).toIntOrNull() == book
        return if (k.any(Char::isUpperCase)) {
            Regex("""(?<![A-Za-z0-9])${Regex.escape(k.trim())}""").containsMatchIn(text)
        } else {
            Regex("""(?<![a-z0-9])${Regex.escape(k)}""", RegexOption.IGNORE_CASE).containsMatchIn(text)
        }
    }

    private val COMMON = setOf(
        "central", "national", "india", "indian", "state", "states", "commission", "committee", "council", "board",
        "authority", "department", "ministry", "institute", "institution", "organisation", "organization", "scheme",
        "mission", "programme", "program", "system", "fund", "society", "agency", "development", "corporation",
        "limited", "union", "office", "officer", "general", "international", "world", "global", "andhra", "pradesh",
        "with", "from", "into", "under", "that", "this", "their", "other",
    )

    /** A meaning defined on another page fits this one when the page uses one of its telling words. */
    private fun fits(full: String, page: String): Boolean =
        Regex("""[a-z]{4,}""").findAll(full.lowercase()).map { it.value }.filter { it !in COMMON }
            .any { Regex("""\b${it.take(6)}""").containsMatchIn(page) }

    /** A source code of the citations (CDI, TH, APPSC ...), not a short form to explain. */
    fun isSourceCode(word: String) = word in CODES || word in NOTE_CODES

    /** Pairs written with a slash, before "/" is read as "or". */
    private fun pairs(text: String): String = text
        .replace(Regex("""\bSCs\s?/\s?STs\b"""), "Scheduled Castes and Scheduled Tribes")
        .replace(Regex("""\bSC\s?/\s?ST\b"""), "Scheduled Caste and Scheduled Tribe")
        .replace(Regex("""\bLS\s?/\s?RS\b"""), "Lok Sabha and Rajya Sabha")

    /** "Chief Justice of India" -> "Chief Justices of India", "Human Development Index" -> "... Indices". */
    private fun pluralOf(s: String): String {
        val of = s.indexOf(" of ")
        if (of > 0) return pluralOf(s.substring(0, of)) + s.substring(of)
        return when {
            s.endsWith("Index") || s.endsWith("index") -> s.dropLast(2) + "ices"
            s.endsWith("gas") -> s + "es"
            s.endsWith("y") && !s.endsWith("ey") -> s.dropLast(1) + "ies"
            s.endsWith("s") -> s
            else -> s + "s"
        }
    }

    private val COURT_WORDS = listOf(
        "judge", "bench", "verdict", "ruled", "rule ", "held", "upheld", "struck", " case", "petition", "cji", "judgment",
        "judgement", "appeal", "collegium", "directed", "observed", "court", " v ", " vs", "versus", "article 32", "writ",
        "constitution bench", "hearing", "pendency", "order", "jurisdiction", "advocate", "chief justice",
    )
    private val CASTE_WORDS = listOf(
        "reserv", "quota", "seats", "communit", "caste", "welfare", "sub-categor", "subcategor", "dalit", "population",
        "student", "women", "famil", "hostel", "sub-plan", "atrocit", "untouchab", "constituenc", "tribe", "backward",
        "scholarship", "households", "colon", "corporation", "beneficiar", "category", "categories",
    )

    /** Short forms whose meaning depends on the words around them or on the subject (book). */
    private fun contextual(token: String, word: String, before: String, after: String, book: Int): String? {
        val prev = before.trimEnd().substringAfterLast(' ').lowercase()
        val plural = token != word
        fun p(s: String, pl: String = s + "s") = if (plural) pl else s
        return when (word) {
            "SC" -> when {
                plural || Regex("""^\s*(/|and|,|-)\s*(ST|BC|OBC)""").containsMatchIn(after) ||
                    Regex("""(ST|BC|OBC)\s*(/|and|,)\s*$""").containsMatchIn(before) -> p("Scheduled Caste")
                // the words right next to it: "SC students" / "the SC held", "challenged in the SC" / "5 lakh SC"
                Regex("""^\s*(\+|commission|finance|development|sub|students|families|women|households|hostel|colon|population|communit|beneficiar|candidates|seats|reservation|quota|sub-plan|component|corporation|welfare|category|categories|persons|people|youth|girls|boys|farmers|entrepreneurs|employees|MLAs|MPs|share|percentage|%|habitation|villages|dalit|groups|sub-caste|sub-classif)""", RegexOption.IGNORE_CASE).containsMatchIn(after) -> "Scheduled Caste"
                Regex("""^\s*(\(|'s|’s|bench|held|ruled|upheld|struck|ordered|directed|said|observed|judg|verdict|order|collegium|judge|stayed|quashed|allowed|dismissed|asked|issued|refused|declined|set aside|noted|clarified|cited|constitution bench|on \d|has |had |will |would |can |may |agreed|sought|flagged|reserved|transferred|appointed|recommend)""", RegexOption.IGNORE_CASE).containsMatchIn(after) ||
                    Regex("""(\bin|before|\bby|moved|approached|challenged in|apex|told|petition in|plea in|appeal to|appealed to|of the|verdict of|judgment of|ruling of|decision of|bench of|judges of|judge of|from the|go to|went to)\s*(the\s*)?$""", RegexOption.IGNORE_CASE).containsMatchIn(before) -> "Supreme Court"
                Regex("""(\d|lakh|crore|for|among|backward|poor|landless|tribal|and the|women of)\s*$""", RegexOption.IGNORE_CASE).containsMatchIn(before) -> "Scheduled Caste"
                else -> {
                    // then the words around: judges and verdicts, or reservation and communities
                    val near = (before.takeLast(90) + " " + after.take(90)).lowercase()
                    val court = COURT_WORDS.count { it in near }
                    val caste = CASTE_WORDS.count { it in near }
                    when {
                        court > caste -> "Supreme Court"
                        caste > court -> "Scheduled Caste"
                        book == 2 || book == 5 -> "Supreme Court"
                        else -> "Scheduled Caste"
                    }
                }
            }
            "ST" -> p("Scheduled Tribe")
            "BC" -> if (Regex("""\d\s*$""").containsMatchIn(before)) "B C" else p("Backward Class", "Backward Classes")
            "MP" -> if (plural || prev in setOf("a", "an", "each", "every", "the", "any", "sitting", "elected", "nominated", "one", "no", "former"))
                p("Member of Parliament", "Members of Parliament") else "Madhya Pradesh"
            "CPI" -> if (book == 1 || (book == 2 && !Regex("""^\s*(inflation|\(|-|basket|combined|rural|urban)""", RegexOption.IGNORE_CASE).containsMatchIn(after)))
                "Communist Party of India" else "Consumer Price Index"
            "CDM" -> if (book == 1) "Civil Disobedience Movement" else "Clean Development Mechanism"
            "CAA" -> if (Regex("""\d(st|nd|rd|th)\s*$""").containsMatchIn(before)) p("Constitutional Amendment Act") else "Citizenship Amendment Act"
            "ASI" -> if (Regex("""ancestr|genetic|genom|ANI\b|DNA""", RegexOption.IGNORE_CASE).containsMatchIn(before.takeLast(120) + after.take(120)))
                "Ancestral South Indians" else "Archaeological Survey of India"
            "RTGS" -> if (Regex("""payment|NEFT|RBI|settlement|transfer|bank""", RegexOption.IGNORE_CASE).containsMatchIn(before.takeLast(120) + after.take(120)) ||
                (book == 3 && !Regex("""governance|AP\b|Andhra|dashboard""").containsMatchIn(before.takeLast(120) + after.take(120))))
                "real-time gross settlement" else "Real Time Governance Society"
            "RE" -> when {
                Regex("""^\s*(XIV|XIII|XII|XI|X|IX|VIII|VII|VI|V|IV|III|II|I)\b""").containsMatchIn(after) -> {
                    "Rock Edict"
                }
                Regex("""\d{4}-\d{2}\)?\s*$""").containsMatchIn(before) || Regex("""^\s*\d{4}-\d{2}""").containsMatchIn(after) -> "Revised Estimates"
                else -> "renewable energy"
            }
            "DM" -> if (Regex("""^\s*(Act|Cell|cycle|plan|policy)""", RegexOption.IGNORE_CASE).containsMatchIn(after) || prev == "on") "disaster management" else "District Magistrate"
            "NH" -> if (Regex("""^\s*(and|or)\s+(the\s+)?SH\b""").containsMatchIn(after) || Regex("""\bSH\s+(and|or)\s+(the\s+)?$""").containsMatchIn(before) || prev == "the" && Regex("""^\s*(and|,)""").containsMatchIn(after))
                "Northern Hemisphere" else "National Highway"
            "LPG" -> if (Regex("""^\s*(reform|model|era|policy|policies)""", RegexOption.IGNORE_CASE).containsMatchIn(after))
                "liberalisation, privatisation and globalisation" else "liquefied petroleum gas"
            else -> null
        }
    }
}
