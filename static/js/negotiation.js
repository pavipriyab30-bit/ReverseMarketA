/**
 * BESTORA FIT
 * AI Negotiation Frontend
 *
 * Handles:
 * - Negotiation strategy
 * - Progressive buyer/seller negotiation
 * - Seller price persistence
 * - Deal acceptance
 * - Counter offers
 * - Walk away
 * - AI negotiation message
 */

"use strict";

/* =========================================================
   GLOBAL STATE
   ========================================================= */

let negotiationStrategy = null;
let negotiationContext = null;

let currentSellerPrice = null;
let currentBuyerOffer = null;

let negotiationRound = 0;
let negotiationStarted = false;


/* =========================================================
   HELPERS
   ========================================================= */

function getElement(id) {
    return document.getElementById(id);
}


function formatPrice(price) {
    const value = Number(price);

    if (!Number.isFinite(value)) {
        return "₹0";
    }

    return `₹${value.toLocaleString("en-IN", {
        maximumFractionDigits: 0
    })}`;
}


function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function roundToFive(value) {
    return Math.round(Number(value) / 5) * 5;
}


function showStrategyStatus(message, type = "info") {

    const element =
        getElement("strategyStatus");

    if (!element) {
        return;
    }

    const classes = {
        info: "alert alert-info",
        success: "alert alert-success",
        warning: "alert alert-warning",
        error: "alert alert-danger"
    };

    element.className =
        classes[type] || classes.info;

    element.textContent = message;
    element.hidden = false;
}


function showSellerStatus(message, type = "info") {

    const element =
        getElement("sellerResponseStatus");

    if (!element) {
        return;
    }

    const classes = {
        info: "alert alert-info",
        success: "alert alert-success",
        warning: "alert alert-warning",
        error: "alert alert-danger"
    };

    element.className =
        classes[type] || classes.info;

    element.textContent = message;
    element.hidden = false;
}


function showMessageStatus(message, type = "info") {

    const element =
        getElement("messageStatus");

    if (!element) {
        return;
    }

    const classes = {
        info: "alert alert-info",
        success: "alert alert-success",
        warning: "alert alert-warning",
        error: "alert alert-danger"
    };

    element.className =
        classes[type] || classes.info;

    element.textContent = message;
    element.hidden = false;
}


function getQueryParameter(name) {

    const params =
        new URLSearchParams(
            window.location.search
        );

    return params.get(name);
}


function getNumberParameter(
    name,
    fallback = 0
) {

    const value =
        Number(
            getQueryParameter(name)
        );

    return Number.isFinite(value)
        ? value
        : fallback;
}


/* =========================================================
   READ SELECTED SERVICE
   ========================================================= */

function getNegotiationContext() {

    return {

        providerName:
            getQueryParameter(
                "provider_name"
            ) ||
            "Service Provider",

        offerTitle:
            getQueryParameter(
                "offer_title"
            ) ||
            "Service",

        originalPrice:
            getNumberParameter(
                "original_price",
                0
            ),

        trustScore:
            getNumberParameter(
                "trust_score",
                50
            ),

        matchScore:
            getNumberParameter(
                "match_score",
                50
            ),

        riskLevel:
            getQueryParameter(
                "risk_level"
            ) ||
            "LOW",

        userRequirement:
            getQueryParameter(
                "user_requirement"
            ) ||
            "",

        budgetMax:
            getNumberParameter(
                "budget_max",
                0
            )
    };
}


/* =========================================================
   RENDER BASIC INFORMATION
   ========================================================= */

function renderNegotiationContext() {

    negotiationContext =
        getNegotiationContext();

    const providerElement =
        getElement("providerName");

    const offerElement =
        getElement("offerTitle");

    const originalPriceInput =
        getElement(
            "originalPriceInput"
        );

    const originalPriceElement =
        getElement("originalPrice");

    const riskElement =
        getElement("riskBadge");

    if (providerElement) {

        providerElement.textContent =
            negotiationContext.providerName;
    }

    if (offerElement) {

        offerElement.textContent =
            negotiationContext.offerTitle;
    }

    if (originalPriceInput) {

        originalPriceInput.value =
            negotiationContext.originalPrice;
    }

    if (originalPriceElement) {

        originalPriceElement.textContent =
            formatPrice(
                negotiationContext.originalPrice
            );
    }

    if (riskElement) {

        riskElement.textContent =
            `${negotiationContext.riskLevel} RISK`;
    }
}


/* =========================================================
   STRATEGY
   ========================================================= */

async function createStrategy() {

    const originalPriceInput =
        getElement(
            "originalPriceInput"
        );

    const budgetInput =
        getElement("budgetMax");

    const trustInput =
        getElement("trustScore");

    const matchInput =
        getElement("matchScore");

    if (!originalPriceInput) {
        return null;
    }

    const originalPrice =
        Number(
            originalPriceInput.value
        );

    const budgetMax =
        budgetInput &&
        budgetInput.value.trim() !== ""
            ? Number(
                budgetInput.value
            )
            : null;

    const trustScore =
        trustInput
            ? Number(
                trustInput.value || 0
            )
            : 50;

    const matchScore =
        matchInput
            ? Number(
                matchInput.value || 0
            )
            : 50;


    if (
        !Number.isFinite(
            originalPrice
        ) ||
        originalPrice <= 0
    ) {

        showStrategyStatus(
            "Invalid original price.",
            "warning"
        );

        return null;
    }


    if (
        budgetMax !== null &&
        (
            !Number.isFinite(
                budgetMax
            ) ||
            budgetMax <= 0
        )
    ) {

        showStrategyStatus(
            "Please enter a valid maximum budget.",
            "warning"
        );

        return null;
    }


    showStrategyStatus(
        "Calculating AI negotiation strategy...",
        "info"
    );


    const button =
        getElement(
            "strategyButton"
        );

    if (button) {

        button.disabled = true;

        button.textContent =
            "Calculating...";
    }


    try {

        const response =
            await fetch(
                "/negotiation/strategy",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        original_price:
                            originalPrice,

                        budget_max:
                            budgetMax,

                        trust_score:
                            trustScore,

                        match_score:
                            matchScore
                    })
                }
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                "Unable to create negotiation strategy."
            );
        }


        negotiationStrategy =
            data.strategy;


        renderStrategy(
            negotiationStrategy
        );


        showStrategyStatus(
            "AI negotiation strategy ready.",
            "success"
        );


        currentSellerPrice =
            Number(
                negotiationStrategy.original_price
            );

        currentBuyerOffer = null;

        negotiationRound = 0;

        negotiationStarted = false;


        return negotiationStrategy;


    } catch (error) {

        console.error(
            "Strategy error:",
            error
        );

        showStrategyStatus(
            error.message ||
            "Unable to create negotiation strategy.",
            "error"
        );

        return null;


    } finally {

        if (button) {

            button.disabled = false;

            button.textContent =
                "Calculate Best Offer";
        }
    }
}


/* =========================================================
   RENDER STRATEGY
   ========================================================= */

function renderStrategy(
    strategy
) {

    if (!strategy) {
        return;
    }


    const originalPrice =
        Number(
            strategy.original_price || 0
        );


    /*
     * BESTORA FIT recommended price.
     *
     * Prefer opening_price because that is
     * the recommended starting offer.
     */
    const recommendedPrice =
        Number(
            strategy.opening_price ||
            strategy.target_price ||
            0
        );


    const savingAmount =
        Math.max(
            originalPrice -
            recommendedPrice,
            0
        );


    const savingPercent =
        originalPrice > 0
            ? (
                savingAmount /
                originalPrice
            ) * 100
            : 0;


    const original =
        getElement(
            "originalPrice"
        );

    const originalInput =
        getElement(
            "originalPriceInput"
        );

    const proposed =
        getElement(
            "proposedPrice"
        );

    const discount =
        getElement(
            "discount"
        );

    const recommended =
        getElement(
            "recommendedPrice"
        );

    const potentialSaving =
        getElement(
            "potentialSaving"
        );

    const confidence =
        getElement(
            "intelligenceConfidence"
        );

    const confidenceLevel =
        getElement(
            "intelligenceLevel"
        );

    const maximumSaving =
        getElement(
            "maximumSaving"
        );

    const reason =
        getElement(
            "strategyReason"
        );


    if (original) {

        original.textContent =
            formatPrice(
                originalPrice
            );
    }


    if (originalInput) {

        originalInput.value =
            originalPrice;
    }


    if (recommended) {

        recommended.textContent =
            formatPrice(
                recommendedPrice
            );
    }


    if (proposed) {

        proposed.textContent =
            formatPrice(
                recommendedPrice
            );
    }


    /*
     * IMPORTANT:
     *
     * Potential Saving now shows:
     *
     * ₹129 (10%)
     *
     * instead of only:
     *
     * ₹129
     */
    if (potentialSaving) {

        potentialSaving.textContent =
            `${formatPrice(
                savingAmount
            )} (${savingPercent.toFixed(0)}%)`;
    }


    /*
     * Top-card percentage.
     */
    if (discount) {

        discount.textContent =
            `${savingPercent.toFixed(0)}%`;
    }


    if (confidence) {

        confidence.textContent =
            `${Number(
                strategy.confidence || 0
            ).toFixed(1)}%`;
    }


    if (confidenceLevel) {

        confidenceLevel.textContent =
            strategy.confidence_level ||
            "MEDIUM";
    }


    if (maximumSaving) {

        const maximum =
            Number(
                strategy.maximum_saving ||
                savingAmount
            );

        maximumSaving.textContent =
            formatPrice(
                maximum
            );
    }


    if (reason) {

        reason.textContent =
            strategy.reason ||
            "AI generated a controlled negotiation strategy.";
    }
}


/* =========================================================
   START LIVE NEGOTIATION
   ========================================================= */

function startLiveNegotiation() {

    if (!negotiationStrategy) {

        showStrategyStatus(
            "Create the negotiation strategy first.",
            "warning"
        );

        return;
    }


    /*
     * The first seller price is ALWAYS
     * the exact selected database offer price.
     */
    currentSellerPrice =
        Number(
            negotiationStrategy.original_price
        );


    currentBuyerOffer = null;

    negotiationRound = 0;

    negotiationStarted = true;


    const panel =
        getElement(
            "liveNegotiationPanel"
        );

    if (panel) {

        panel.hidden = false;
    }


    updateSellerPriceDisplay();

    updateRoundDisplay();


    addConversationMessage(
        "system",
        "Negotiation started. The listed price is locked to the selected offer."
    );


    const buyerInput =
        getElement(
            "buyerOfferInput"
        );

    if (buyerInput) {

        buyerInput.value =
            negotiationStrategy.opening_price;

        buyerInput.min = 1;

        buyerInput.focus();
    }


    showSellerStatus(
        "AI recommends starting around " +
        formatPrice(
            negotiationStrategy.opening_price
        ) +
        ".",
        "info"
    );
}


/* =========================================================
   UPDATE SELLER PRICE DISPLAY
   ========================================================= */

function updateSellerPriceDisplay() {

    const element =
        getElement(
            "currentSellerPrice"
        );

    if (!element) {
        return;
    }

    element.textContent =
        formatPrice(
            currentSellerPrice
        );
}


/* =========================================================
   UPDATE ROUND
   ========================================================= */

function updateRoundDisplay() {

    const element =
        getElement(
            "negotiationRoundBadge"
        );

    if (!element) {
        return;
    }

    element.textContent =
        `Round ${negotiationRound}`;
}


/* =========================================================
   CONVERSATION
   ========================================================= */

function addConversationMessage(
    speaker,
    message
) {

    const container =
        getElement(
            "negotiationConversation"
        );

    if (!container) {
        return;
    }


    const wrapper =
        document.createElement(
            "div"
        );


    let label = "AI";


    if (speaker === "buyer") {

        label = "YOU";

    } else if (
        speaker === "seller"
    ) {

        label = "SELLER";

    } else if (
        speaker === "system"
    ) {

        label = "BESTORA FIT";
    }


    /*
     * BUYER:
     * right side
     */
    if (speaker === "buyer") {

        wrapper.className =
            "negotiation-message mb-3 d-flex justify-content-end";


        wrapper.innerHTML = `

            <div
                style="
                    max-width: 75%;
                    text-align: right;
                "
            >

                <div
                    class="small fw-bold text-primary mb-1"
                >
                    ${escapeHtml(label)}
                </div>


                <div
                    class="p-3 rounded-4 border bg-primary text-white"
                    style="
                        display: inline-block;
                        text-align: left;
                        border-bottom-right-radius: 6px !important;
                    "
                >
                    ${escapeHtml(message)}
                </div>

            </div>
        `;


    /*
     * SELLER:
     * left side
     */
    } else if (
        speaker === "seller"
    ) {

        wrapper.className =
            "negotiation-message mb-3 d-flex justify-content-start";


        wrapper.innerHTML = `

            <div
                style="
                    max-width: 75%;
                    text-align: left;
                "
            >

                <div
                    class="small fw-bold text-muted mb-1"
                >
                    ${escapeHtml(label)}
                </div>


                <div
                    class="p-3 rounded-4 border bg-light"
                    style="
                        display: inline-block;
                        text-align: left;
                        border-bottom-left-radius: 6px !important;
                    "
                >
                    ${escapeHtml(message)}
                </div>

            </div>
        `;


    /*
     * SYSTEM:
     * centered
     */
    } else {

        wrapper.className =
            "negotiation-message mb-3 d-flex justify-content-center";


        wrapper.innerHTML = `

            <div
                style="
                    max-width: 80%;
                    text-align: center;
                "
            >

                <div
                    class="small fw-bold text-muted mb-1"
                >
                    ${escapeHtml(label)}
                </div>


                <div
                    class="p-3 rounded-4 border bg-light text-muted"
                    style="
                        display: inline-block;
                        text-align: center;
                    "
                >
                    ${escapeHtml(message)}
                </div>

            </div>
        `;
    }


    container.appendChild(
        wrapper
    );


    container.scrollTop =
        container.scrollHeight;
}


/* =========================================================
   SEND BUYER OFFER
   ========================================================= */

async function sendBuyerOffer() {

    if (!negotiationStarted) {

        startLiveNegotiation();

        return;
    }


    const input =
        getElement(
            "buyerOfferInput"
        );

    if (!input) {
        return;
    }


    const buyerOffer =
        Number(
            input.value
        );


    const originalPrice =
        Number(
            negotiationStrategy.original_price
        );


    if (
        !Number.isFinite(
            buyerOffer
        ) ||
        buyerOffer <= 0
    ) {

        showSellerStatus(
            "Enter a valid offer.",
            "warning"
        );

        input.focus();

        return;
    }


    if (
        buyerOffer >
        originalPrice
    ) {

        showSellerStatus(
            "Your offer cannot exceed the listed price.",
            "warning"
        );

        return;
    }


    if (
        currentBuyerOffer !== null &&
        buyerOffer ===
        currentBuyerOffer
    ) {

        showSellerStatus(
            "Increase your offer slightly to continue.",
            "warning"
        );

        return;
    }


    /*
     * Buyer offering at or above seller price
     * means immediate acceptance.
     */
    if (
        currentSellerPrice !== null &&
        buyerOffer >=
        currentSellerPrice
    ) {

        currentBuyerOffer =
            buyerOffer;


        addConversationMessage(
            "buyer",
            `I can offer ${formatPrice(
                buyerOffer
            )}.`
        );


        addConversationMessage(
            "seller",
            `The seller accepted your offer of ${formatPrice(
                buyerOffer
            )}.`
        );


        await acceptDealAtPrice(
            buyerOffer
        );

        return;
    }


    /*
     * Save the CURRENT seller price.
     *
     * This is important for progressive
     * seller negotiation.
     */
    const previousSellerPrice =
        Number(
            currentSellerPrice
        );


    currentBuyerOffer =
        buyerOffer;


    addConversationMessage(
        "buyer",
        `I can offer ${formatPrice(
            buyerOffer
        )}.`
    );


    const button =
        getElement(
            "sendBuyerOfferButton"
        );

    if (button) {

        button.disabled = true;

        button.textContent =
            "Seller is responding...";
    }


    try {

        const response =
            await fetch(
                "/negotiation/seller-counter",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        original_price:
                            originalPrice,

                        buyer_offer:
                            buyerOffer,

                        trust_score:
                            Number(
                                negotiationStrategy.trust_score ||
                                getNumberParameter(
                                    "trust_score",
                                    50
                                )
                            ),

                        match_score:
                            Number(
                                negotiationStrategy.match_score ||
                                getNumberParameter(
                                    "match_score",
                                    50
                                )
                            ),

                        previous_seller_price:
                            previousSellerPrice,

                        negotiation_round:
                            negotiationRound + 1
                    })
                }
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                "Seller negotiation failed."
            );
        }


        negotiationRound += 1;

        updateRoundDisplay();


        const result =
            data.result ||
            data.counter ||
            data;


        const sellerPrice =
            Number(
                result.seller_price
            );


        if (
            !Number.isFinite(
                sellerPrice
            )
        ) {

            throw new Error(
                "Seller returned an invalid price."
            );
        }


        /*
         * Seller price MUST NEVER increase.
         */
        if (
            sellerPrice >
            previousSellerPrice
        ) {

            console.error(
                "Invalid seller increase:",
                {
                    previousSellerPrice,
                    sellerPrice,
                    buyerOffer
                }
            );


            showSellerStatus(
                "Seller response was invalid. The seller price cannot increase.",
                "error"
            );

            return;
        }


        /*
         * Seller price also cannot go below
         * the buyer's current offer.
         */
        currentSellerPrice =
            Math.max(
                buyerOffer,
                sellerPrice
            );


        updateSellerPriceDisplay();


        const status =
            String(
                result.status ||
                "COUNTER"
            ).toUpperCase();


        const sellerMessage =
            result.message ||
            `The seller countered at ${formatPrice(
                currentSellerPrice
            )}.`;


        addConversationMessage(
            "seller",
            sellerMessage
        );


        if (
            status === "ACCEPT"
        ) {

            await acceptDealAtPrice(
                currentSellerPrice
            );

            return;
        }


        if (
            status ===
            "NEAR_AGREEMENT"
        ) {

            showSellerStatus(
                sellerMessage,
                "success"
            );


            showDealAnalysis(
                "You are very close.",
                "The buyer and seller prices are nearly aligned. You can accept the current seller price or make one final counter."
            );


        } else if (
            status ===
            "SELLER_FIRM"
        ) {

            showSellerStatus(
                sellerMessage,
                "warning"
            );


            showDealAnalysis(
                "Seller is holding firm.",
                "The seller has stopped making meaningful concessions. Compare the current price with your budget before continuing."
            );


        } else {

            showSellerStatus(
                sellerMessage,
                "info"
            );


            showDealAnalysis(
                "Negotiation progressing.",
                `The seller moved from ${formatPrice(
                    previousSellerPrice
                )} to ${formatPrice(
                    currentSellerPrice
                )}.`
            );
        }


        input.value = "";

        input.focus();


    } catch (error) {

        console.error(
            "Seller counter error:",
            error
        );


        showSellerStatus(
            error.message ||
            "Unable to continue negotiation.",
            "error"
        );


    } finally {

        if (button) {

            button.disabled = false;

            button.textContent =
                "Send Offer";
        }
    }
}


/* =========================================================
   COUNTER AGAIN
   ========================================================= */

function counterAgain() {

    if (
        currentSellerPrice === null ||
        !Number.isFinite(
            Number(
                currentSellerPrice
            )
        )
    ) {

        showSellerStatus(
            "There is no active seller offer.",
            "warning"
        );

        return;
    }


    const previousOffer =
        currentBuyerOffer !== null
            ? Number(
                currentBuyerOffer
            )
            : Number(
                negotiationStrategy.opening_price
            );


    let movementRate =
        0.40;


    if (
        negotiationRound >= 3
    ) {

        movementRate =
            0.50;
    }


    if (
        negotiationRound >= 4
    ) {

        movementRate =
            0.60;
    }


    const gap =
        currentSellerPrice -
        previousOffer;


    if (gap <= 0) {

        acceptDealAtPrice(
            currentSellerPrice
        );

        return;
    }


    let nextOffer =
        previousOffer +
        (
            gap *
            movementRate
        );


    nextOffer =
        roundToFive(
            nextOffer
        );


    if (
        nextOffer <=
        previousOffer
    ) {

        nextOffer =
            previousOffer + 5;
    }


    if (
        nextOffer >=
        currentSellerPrice
    ) {

        nextOffer =
            currentSellerPrice - 5;
    }


    nextOffer =
        Math.max(
            5,
            nextOffer
        );


    const input =
        getElement(
            "buyerOfferInput"
        );


    if (input) {

        input.value =
            Math.round(
                nextOffer
            );

        input.focus();
    }


    showSellerStatus(
        `AI suggests ${formatPrice(
            nextOffer
        )} as your next counter.`,
        "info"
    );
}


/* =========================================================
   ACCEPT DEAL
   ========================================================= */

async function acceptCurrentDeal() {

    if (
        currentSellerPrice === null ||
        !Number.isFinite(
            Number(
                currentSellerPrice
            )
        )
    ) {

        showSellerStatus(
            "There is no active deal to accept.",
            "warning"
        );

        return;
    }


    await acceptDealAtPrice(
        currentSellerPrice
    );
}


async function acceptDealAtPrice(
    finalPrice
) {

    const originalPrice =
        Number(
            negotiationStrategy.original_price
        );


    finalPrice =
        Number(
            finalPrice
        );


    if (
        !Number.isFinite(
            finalPrice
        ) ||
        finalPrice <= 0
    ) {

        showSellerStatus(
            "Invalid final price.",
            "error"
        );

        return;
    }


    const button =
        getElement(
            "acceptDealButton"
        );


    if (button) {

        button.disabled = true;

        button.textContent =
            "Finalizing...";
    }


    try {

        const budgetInput =
            getElement(
                "budgetMax"
            );


        const budgetMax =
            budgetInput &&
            budgetInput.value.trim() !== ""
                ? Number(
                    budgetInput.value
                )
                : null;


        const response =
            await fetch(
                "/negotiation/finalize",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        original_price:
                            originalPrice,

                        final_price:
                            finalPrice,

                        budget_max:
                            budgetMax
                    })
                }
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                data.error ||
                "Unable to finalize deal."
            );
        }


        renderDealConfirmation(
            data
        );


        addConversationMessage(
            "seller",
            `Deal accepted at ${formatPrice(
                finalPrice
            )}.`
        );


        showSellerStatus(
            `Deal accepted at ${formatPrice(
                finalPrice
            )}.`,
            "success"
        );


    } catch (error) {

        console.error(
            "Finalize error:",
            error
        );


        showSellerStatus(
            error.message ||
            "Unable to finalize the deal.",
            "error"
        );


    } finally {

        if (button) {

            button.disabled = false;

            button.textContent =
                "Accept Deal";
        }
    }
}


/* =========================================================
   DEAL CONFIRMATION
   ========================================================= */

function renderDealConfirmation(
    data
) {

    const card =
        getElement(
            "dealConfirmationCard"
        );

    if (card) {

        card.hidden = false;
    }


    const finalPrice =
        getElement(
            "finalDealPrice"
        );

    const savings =
        getElement(
            "finalDealSavings"
        );

    const budgetWarning =
        getElement(
            "finalDealBudgetWarning"
        );

    const budgetWarningText =
        getElement(
            "finalDealBudgetWarningText"
        );

    const status =
        getElement(
            "dealConfirmationStatus"
        );


    if (finalPrice) {

        finalPrice.textContent =
            formatPrice(
                data.final_price
            );
    }


    if (savings) {

        const finalSavings =
            Number(
                data.savings || 0
            );

        const original =
            Number(
                negotiationStrategy?.original_price || 0
            );

        const percent =
            original > 0
                ? (
                    finalSavings /
                    original
                ) * 100
                : 0;

        savings.textContent =
            `${formatPrice(
                finalSavings
            )} (${percent.toFixed(0)}%)`;
    }


    if (
        data.budget_warning
    ) {

        if (budgetWarning) {
            budgetWarning.hidden = false;
        }

        if (budgetWarningText) {

            budgetWarningText.textContent =
                "The final negotiated price is above your maximum budget.";
        }

    } else {

        if (budgetWarning) {
            budgetWarning.hidden = true;
        }
    }


    if (status) {

        status.textContent =
            data.message ||
            "Deal successfully accepted.";

        status.className =
            "alert alert-success";
    }
}


/* =========================================================
   DEAL ANALYSIS
   ========================================================= */

function showDealAnalysis(
    title,
    message
) {

    const panel =
        getElement(
            "aiDealAnalysis"
        );

    const titleElement =
        getElement(
            "aiDealAnalysisTitle"
        );

    const textElement =
        getElement(
            "aiDealAnalysisText"
        );


    if (panel) {
        panel.hidden = false;
    }


    if (titleElement) {

        titleElement.textContent =
            title;
    }


    if (textElement) {

        textElement.textContent =
            message;
    }
}


/* =========================================================
   WALK AWAY
   ========================================================= */

function walkAway() {

    showSellerStatus(
        "Negotiation ended. No deal was accepted.",
        "warning"
    );


    const input =
        getElement(
            "buyerOfferInput"
        );

    if (input) {
        input.disabled = true;
    }


    const sendButton =
        getElement(
            "sendBuyerOfferButton"
        );

    if (sendButton) {
        sendButton.disabled = true;
    }


    const counterButton =
        getElement(
            "counterAgainButton"
        );

    if (counterButton) {
        counterButton.disabled = true;
    }


    const acceptButton =
        getElement(
            "acceptDealButton"
        );

    if (acceptButton) {
        acceptButton.disabled = true;
    }


    addConversationMessage(
        "system",
        "You chose to walk away from the negotiation."
    );
}


/* =========================================================
   GENERATE AI MESSAGE
   ========================================================= */

async function generateNegotiationMessage() {

    const context =
        getNegotiationContext();


    const originalPrice =
        Number(
            getElement(
                "originalPriceInput"
            )?.value || 0
        );


    const proposedPrice =
        currentBuyerOffer !== null
            ? Number(
                currentBuyerOffer
            )
            : Number(
                negotiationStrategy?.opening_price ||
                0
            );


    if (
        !Number.isFinite(
            originalPrice
        ) ||
        originalPrice <= 0
    ) {

        showMessageStatus(
            "Calculate the negotiation strategy first.",
            "warning"
        );

        return;
    }


    if (
        !Number.isFinite(
            proposedPrice
        ) ||
        proposedPrice <= 0
    ) {

        showMessageStatus(
            "Enter a valid negotiation offer first.",
            "warning"
        );

        return;
    }


    const button =
        getElement(
            "generateMessageButton"
        );


    if (button) {

        button.disabled = true;

        button.textContent =
            "Generating...";
    }


    try {

        const response =
            await fetch(
                "/negotiation/message",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        provider_name:
                            context.providerName,

                        offer_title:
                            context.offerTitle,

                        original_price:
                            originalPrice,

                        proposed_price:
                            proposedPrice,

                        user_requirement:
                            context.userRequirement
                    })
                }
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                "Unable to generate negotiation message."
            );
        }


        const messageElement =
            getElement(
                "negotiationMessage"
            );


        if (messageElement) {

            messageElement.value =
                data.message || "";
        }


        showMessageStatus(
            "Negotiation message generated.",
            "success"
        );


    } catch (error) {

        console.error(
            "Message generation error:",
            error
        );


        showMessageStatus(
            error.message ||
            "Unable to generate message.",
            "error"
        );


    } finally {

        if (button) {

            button.disabled = false;

            button.textContent =
                "Generate Message";
        }
    }
}


/* =========================================================
   COPY MESSAGE
   ========================================================= */

async function copyNegotiationMessage() {

    const element =
        getElement(
            "negotiationMessage"
        );


    if (!element) {
        return;
    }


    const message =
        element.value.trim();


    if (!message) {

        showMessageStatus(
            "There is no message to copy.",
            "warning"
        );

        return;
    }


    try {

        await navigator.clipboard.writeText(
            message
        );


        showMessageStatus(
            "Message copied to clipboard.",
            "success"
        );


    } catch (error) {

        element.focus();

        element.select();

        document.execCommand(
            "copy"
        );


        showMessageStatus(
            "Message copied to clipboard.",
            "success"
        );
    }
}


/* =========================================================
   PROCEED TO BILLING
   ========================================================= */

function proceedToBilling() {

    const context =
        negotiationContext ||
        getNegotiationContext();


    const finalPrice =
        Number(
            currentBuyerOffer ||
            currentSellerPrice ||
            0
        );


    const originalPrice =
        Number(
            context.originalPrice ||
            0
        );


    const savings =
        Math.max(
            originalPrice -
            finalPrice,
            0
        );


    const budget =
        Number(
            getElement(
                "budgetMax"
            )?.value || 0
        );


    const params =
        new URLSearchParams({

            provider_name:
                context.providerName ||
                "",

            offer_title:
                context.offerTitle ||
                "",

            original_price:
                String(
                    originalPrice
                ),

            final_price:
                String(
                    finalPrice
                ),

            savings:
                String(
                    savings
                ),

            budget_warning:
                (
                    budget > 0 &&
                    finalPrice > budget
                )
                    ? "true"
                    : "false"
        });


    window.location.href =
        `/negotiation/billing?${params.toString()}`;
}


/* =========================================================
   INITIALIZATION
   ========================================================= */

function initializeNegotiationPage() {

    renderNegotiationContext();


    const strategyButton =
        getElement(
            "strategyButton"
        );

    const sendBuyerOfferButton =
        getElement(
            "sendBuyerOfferButton"
        );

    const acceptDealButton =
        getElement(
            "acceptDealButton"
        );

    const counterAgainButton =
        getElement(
            "counterAgainButton"
        );

    const walkAwayButton =
        getElement(
            "walkAwayButton"
        );

    const generateMessageButton =
        getElement(
            "generateMessageButton"
        );

    const copyMessageButton =
        getElement(
            "copyMessageButton"
        );

    const proceedBillingButton =
        getElement(
            "proceedBillingButton"
        );


    if (strategyButton) {

        strategyButton.addEventListener(
            "click",
            async function () {

                const strategy =
                    await createStrategy();

                if (strategy) {

                    startLiveNegotiation();
                }
            }
        );
    }


    if (sendBuyerOfferButton) {

        sendBuyerOfferButton.addEventListener(
            "click",
            sendBuyerOffer
        );
    }


    if (acceptDealButton) {

        acceptDealButton.addEventListener(
            "click",
            acceptCurrentDeal
        );
    }


    if (counterAgainButton) {

        counterAgainButton.addEventListener(
            "click",
            counterAgain
        );
    }


    if (walkAwayButton) {

        walkAwayButton.addEventListener(
            "click",
            walkAway
        );
    }


    if (generateMessageButton) {

        generateMessageButton.addEventListener(
            "click",
            generateNegotiationMessage
        );
    }


    if (copyMessageButton) {

        copyMessageButton.addEventListener(
            "click",
            copyNegotiationMessage
        );
    }


    if (proceedBillingButton) {

        proceedBillingButton.addEventListener(
            "click",
            proceedToBilling
        );
    }


    const buyerInput =
        getElement(
            "buyerOfferInput"
        );


    if (buyerInput) {

        buyerInput.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    sendBuyerOffer();
                }
            }
        );
    }


    console.log(
        "BESTORA FIT negotiation frontend initialized."
    );
}


/* =========================================================
   START
   ========================================================= */

if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initializeNegotiationPage
    );

} else {

    initializeNegotiationPage();
} 