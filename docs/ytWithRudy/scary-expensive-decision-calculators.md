# Scary Expensive Decision Calculators — Master List

**Product concept:** A small web app hosting a suite of "scary expensive decision" calculators.
**Target market:** US buyers, built & operated from India (digital delivery, USD pricing, no shipping).
**Core principle (from Richard Yu):** A budget tracker protects $40. A rental property calculator protects a $200,000 decision. Same effort to build — but you charge $10 for one and $99 for the other. **The whole game is picking a buyer whose mistake is expensive.**

**Ranking logic:** Each calculator is scored on the size of the decision it protects (the price anchor), how terrified the buyer is of getting it wrong, how clear/identifiable the buyer is, and build difficulty.

---

## 🏆 Tier 1 — Protects $100,000+ decisions (highest price point, clearest terrified buyer)

These are the ones you can charge $79–$200 for, or bundle into a subscription. The buyer is making a life-altering financial decision and is terrified of getting it wrong.

| # | Calculator | Decision protected | Target buyer | Why it's scary |
|---|-----------|-------------------|--------------|----------------|
| 1 | **Rental Property Analyzer** | $150k–$500k property purchase | First-time real estate investors | One wrong number = years of negative cash flow |
| 2 | **House-Flip Profit Calculator** | $50k–$300k flip | House flippers | Underestimating rehab costs kills the whole deal |
| 3 | **Business Valuation / Buy-a-Business** | $100k–$1M+ | Someone buying a small business | Overpaying by 10% = $50k+ mistake |
| 4 | **Refinance Break-Even Calculator** | $200k–$500k mortgage | Homeowners considering refi | Closing costs can wipe out years of savings |
| 5 | **Rent vs Buy Calculator** | $200k+ | First-time home buyers | Buying too early or renting too long both cost tens of thousands |
| 6 | **College ROI / Student Loan Decision** | $50k–$200k education cost | High schoolers & parents | $100k of debt for a degree that won't pay it back |
| 7 | **Retirement / 401k Rollover** | $100k–$1M+ | Mid-career professionals changing jobs | A rollover mistake can trigger taxes + penalties |
| 8 | **Commercial Real Estate / Lease Analysis** | $100k–$1M+ | Small business owners leasing space | A 5-year lease at the wrong rate is a fortune |

---

## 🥈 Tier 2 — Protects $10k–$100k decisions (strong price point, $49–$99)

Clear buyers, big enough stakes to justify a real price, but slightly less "life-altering" than Tier 1.

| # | Calculator | Decision protected | Target buyer | Why it's scary |
|---|-----------|-------------------|--------------|----------------|
| 9 | **Car Purchase: Buy vs Lease / New vs Used** | $20k–$60k | Car buyers | A bad deal compounds for 5+ years |
| 10 | **Solar Panel ROI** | $15k–$40k | Homeowners | Payback period can be 5–15 years; hard to verify claims |
| 11 | **EV vs Gas Total Cost** | $30k–$60k | Car buyers | Upfront premium vs long-term savings is confusing |
| 12 | **Debt Avalanche vs Snowball** | $10k–$100k | People with multiple debts | Wrong order = thousands in extra interest |
| 13 | **Student Loan Refinance** | $20k–$150k | Recent grads | Refinancing federal loans can lose protections forever |
| 14 | **Insurance: Term vs Whole Life** | $10k–$100k+ lifetime | Young families | Whole life is often a terrible deal; agents push it |
| 15 | **Hiring vs Outsourcing / Freelance** | $30k–$150k/yr | Small business owners | A full-time hire is a $100k+ commitment |
| 16 | **Equipment Purchase ROI** | $10k–$100k | Tradespeople, manufacturers | Buying vs leasing equipment is a big capital decision |
| 17 | **Franchise ROI** | $50k–$500k | Aspiring franchise owners | Franchise fees + royalties can eat all profit |
| 18 | **Relocation Cost Calculator** | $10k–$50k | People moving for a job | Moving costs + cost-of-living change is a huge decision |

---

## 🥉 Tier 3 — Protects $1k–$10k decisions (entry price point, $19–$49)

Easier to build, higher volume, good for filling out the app and driving traffic. These are the "foot in the door" calculators.

| # | Calculator | Decision protected | Target buyer | Why it's scary |
|---|-----------|-------------------|--------------|----------------|
| 19 | **Pricing Calculator for a Small Online Store** | $1k–$10k/mo revenue | Etsy/Etsy sellers, small shops | Wrong pricing = no profit or no sales |
| 20 | **Wedding Budget Calculator** | $10k–$40k | Engaged couples | Average US wedding is $30k+; easy to blow past |
| 21 | **Medical Procedure Cost / Surgery Decision** | $1k–$20k | Patients with high deductibles | Out-of-network or surprise billing = huge cost |
| 22 | **LASIK / Dental Implant / IVF Cost** | $2k–$20k | People considering elective procedures | Big out-of-pocket, hard to compare providers |
| 23 | **Home Renovation ROI** | $5k–$50k | Homeowners | A $30k kitchen remodel may only add $15k to value |
| 24 | **Property Tax Appeal** | $1k–$10k/yr | Homeowners | Over-assessed property = overpaying every year |
| 25 | **Salary Negotiation / Job Offer Evaluator** | $5k–$50k/yr | Job seekers | Leaving $10k on the table compounds for years |
| 26 | **Side Hustle Viability** | $1k–$10k | Aspiring entrepreneurs | Time + money invested in a hustle that won't work |
| 27 | **LLC vs Sole Proprietor** | $1k–$10k/yr in taxes | Freelancers, small business | Wrong entity = overpaying taxes or liability risk |
| 28 | **Itemize vs Standard Deduction** | $1k–$10k | US taxpayers | Choosing wrong = overpaying taxes every year |

---

## 🎯 Recommended Starting Set (build these first)

Based on the video's advice — **pick ONE and finish it** — but for an app, the smart play is a **core anchor calculator + 2–3 supporting ones** that share the same codebase and buyer.

**Best first anchor: #1 Rental Property Analyzer**
- Protects the biggest decision ($150k–$500k)
- Clear, identifiable, high-intent buyer (real estate investors)
- Well-understood math (NOI, cap rate, cash-on-cash return, 1% rule)
- High price point ($99–$200) or subscription
- Huge existing demand — every real estate investor searches for this

**Supporting calculators that share the same buyer (real estate investors):**
- #2 House-Flip Profit Calculator
- #4 Refinance Break-Even
- #5 Rent vs Buy

**Why this cluster:** One buyer (real estate investors), one domain (real estate), one codebase. You build the app once, add calculators incrementally, and cross-sell. This is the "vertical beats general" principle from the video — a real-estate-decision calculator app, not a generic calculator app.

---

## 📐 App Architecture (proposal)

- **Type:** Small web app (SaaS-style), hosted, USD pricing
- **Stack (local-first, buildable from India):** Next.js/React frontend + a lightweight backend (or fully static with client-side JS for the calculators). No heavy infra needed.
- **Monetization:** Free tier (1–2 basic calculators) → paid tier (full suite) → premium (advanced real-estate calculators). Or one-time purchase per calculator.
- **US-market positioning:** USD pricing, US tax/legal/real-estate conventions baked in, US-focused content/SEO.
- **Delivery:** No shipping, no inventory — pure digital. Perfect for India→US.

---

## 📌 Next Steps (pick one to proceed)

1. **Build the Rental Property Analyzer app** (anchor calculator) — I can scaffold the project
2. **Validate first** — one-page landing page + Buy Now button, test in real-estate Facebook groups (the "collect money first" move from the video)
3. **Expand the list** — add more calculators or refine the real-estate cluster
4. **Different starting niche** — if real estate isn't the right buyer for you, pick another Tier 1 calculator
