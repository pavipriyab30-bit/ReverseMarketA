 /**
 * BESTORA FIT
 * Main application JavaScript
 *
 * Handles:
 * - Service requirement submission
 * - Communication with /service/match
 * - Loading and error states
 * - Rendering provider matches
 * - Opening negotiation for a selected offer
 */


/* =========================================================
   DOM HELPERS
   ========================================================= */

function getElement(id) {
    return document.getElementById(id);
}


/* =========================================================
   STATUS DISPLAY
   ========================================================= */

function showStatus(message, type = "info") {
    const statusElement = getElement("serviceStatus");

    if (!statusElement) {
        return;
    }

    const typeClasses = {
        info: "alert alert-info",
        success: "alert alert-success",
        warning: "alert alert-warning",
        error: "alert alert-danger"
    };

    statusElement.className =
        typeClasses[type] || typeClasses.info;

    statusElement.textContent = message;
    statusElement.hidden = false;
}


function hideStatus() {
    const statusElement = getElement("serviceStatus");

    if (!statusElement) {
        return;
    }

    statusElement.hidden = true;
    statusElement.textContent = "";
}


/* =========================================================
   LOADING STATE
   ========================================================= */

function setLoading(isLoading) {
    const form = getElement("serviceForm");

    if (!form) {
        return;
    }

    const button = form.querySelector(
        'button[type="submit"]'
    );

    if (!button) {
        return;
    }

    if (isLoading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = "Finding Best Matches...";
    } else {
        button.disabled = false;

        if (button.dataset.originalText) {
            button.textContent = button.dataset.originalText;
        }
    }
}


/* =========================================================
   HTML SAFETY
   ========================================================= */

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


/* =========================================================
   URL PARAMETER SAFETY
   ========================================================= */

function encodeParameter(value) {
    return encodeURIComponent(
        value === null || value === undefined
            ? ""
            : String(value)
    );
}


/* =========================================================
   FORMATTING
   ========================================================= */

function formatPrice(price, currency = "INR") {
    if (
        price === null ||
        price === undefined ||
        Number.isNaN(Number(price))
    ) {
        return "Price unavailable";
    }

    const numericPrice = Number(price);

    if (currency === "INR") {
        return `₹${numericPrice.toLocaleString("en-IN")}`;
    }

    return `${currency} ${numericPrice.toLocaleString()}`;
}


function getRiskClass(riskLevel) {
    const level = String(
        riskLevel || "LOW"
    ).toUpperCase();

    if (level === "CRITICAL" || level === "HIGH") {
        return "text-bg-danger";
    }

    if (level === "MEDIUM") {
        return "text-bg-warning";
    }

    return "text-bg-success";
}


function getTrustClass(trustLevel) {
    const level = String(
        trustLevel || ""
    ).toLowerCase();

    if (level === "excellent") {
        return "text-bg-success";
    }

    if (level === "good") {
        return "text-bg-primary";
    }

    if (level === "average") {
        return "text-bg-warning";
    }

    return "text-bg-secondary";
}


/* =========================================================
   REQUIREMENT DISPLAY
   ========================================================= */

function renderRequirement(requirement) {
    if (!requirement) {
        return "";
    }

    const category = escapeHtml(
        requirement.category || "Not specified"
    );

    const location = escapeHtml(
        requirement.location || "Not specified"
    );

    const budget =
        requirement.budget_max !== null &&
        requirement.budget_max !== undefined
            ? formatPrice(requirement.budget_max)
            : "Not specified";

    const urgency = escapeHtml(
        requirement.urgency || "Not specified"
    );

    return `
        <div class="card border-0 bg-light rounded-4 mb-4">
            <div class="card-body p-4">

                <h5 class="fw-bold mb-3">
                    Requirement understood
                </h5>

                <div class="row g-3">

                    <div class="col-md-3">
                        <div class="small text-muted">
                            Category
                        </div>

                        <div class="fw-semibold">
                            ${category}
                        </div>
                    </div>

                    <div class="col-md-3">
                        <div class="small text-muted">
                            Location
                        </div>

                        <div class="fw-semibold">
                            ${location}
                        </div>
                    </div>

                    <div class="col-md-3">
                        <div class="small text-muted">
                            Budget
                        </div>

                        <div class="fw-semibold">
                            ${budget}
                        </div>
                    </div>

                    <div class="col-md-3">
                        <div class="small text-muted">
                            Urgency
                        </div>

                        <div class="fw-semibold text-capitalize">
                            ${urgency}
                        </div>
                    </div>

                </div>

            </div>
        </div>
    `;
}


/* =========================================================
   MATCH CARD
   ========================================================= */

function renderMatch(match, index) {

    const provider = match.provider || {};
    const offer = match.offer || {};

    const providerName = escapeHtml(
        provider.name || "Unknown Provider"
    );

    const offerTitle = escapeHtml(
        offer.title || "Service Offer"
    );

    const description = escapeHtml(
        offer.description ||
        provider.description ||
        "No description available."
    );

    const matchScore = Number(
        match.match_score || 0
    ).toFixed(1);

    const trustScore = Number(
        match.trust_score || 0
    ).toFixed(1);

    const riskScore = Number(
        match.risk_score || 0
    ).toFixed(0);

    const trustLevel = escapeHtml(
        match.trust_level || "Unknown"
    );

    const riskLevel = escapeHtml(
        match.risk_level || "LOW"
    );

    const trustClass = getTrustClass(
        match.trust_level
    );

    const riskClass = getRiskClass(
        match.risk_level
    );

    const price = formatPrice(
        offer.price,
        offer.currency || "INR"
    );

    const deliveryTime = escapeHtml(
        offer.delivery_time || "Not specified"
    );

    const location = escapeHtml(
        provider.location || "Location unavailable"
    );

    const reason = escapeHtml(
        match.recommendation_reason ||
        "Good overall match."
    );

    const riskAlerts = Array.isArray(
        match.risk_alerts
    )
        ? match.risk_alerts
        : [];


    /*
     * Build the negotiation URL.
     *
     * Only create the button when an actual offer
     * with a valid price exists.
     */

    let negotiationButton = "";

    if (
        offer.id !== null &&
        offer.id !== undefined &&
        Number(offer.price) > 0
    ) {

        const negotiationUrl =
            "/negotiation/?" +
            `provider_name=${encodeParameter(provider.name)}` +
            `&offer_title=${encodeParameter(offer.title)}` +
            `&original_price=${encodeParameter(offer.price)}` +
            `&trust_score=${encodeParameter(match.trust_score || 0)}` +
            `&match_score=${encodeParameter(match.match_score || 0)}` +
            `&risk_level=${encodeParameter(match.risk_level || "LOW")}`;

        negotiationButton = `
            <a
                href="${negotiationUrl}"
                class="btn btn-primary"
            >
                Negotiate Better Price
            </a>
        `;
    }


    const alertsHtml = riskAlerts.length > 0
        ? `
            <div class="mt-3">

                <div class="small fw-semibold mb-2">
                    Risk alerts
                </div>

                ${riskAlerts
                    .slice(0, 3)
                    .map(
                        (alert) => `
                            <div class="small text-muted mb-1">
                                • ${escapeHtml(
                                    alert.message ||
                                    "Risk indicator detected."
                                )}
                            </div>
                        `
                    )
                    .join("")
                }

            </div>
        `
        : "";


    return `
        <div class="card border-0 shadow-sm rounded-4 mb-4">

            <div class="card-body p-4">

                <!-- Header -->

                <div class="d-flex flex-column flex-md-row
                            justify-content-between gap-3">

                    <div>

                        <div class="d-flex align-items-center
                                    gap-2 mb-2">

                            <span class="badge text-bg-dark">
                                #${index + 1}
                            </span>

                            <span class="badge ${trustClass}">
                                ${trustLevel} Trust
                            </span>

                            <span class="badge ${riskClass}">
                                ${riskLevel} Risk
                            </span>

                        </div>

                        <h4 class="fw-bold mb-1">
                            ${providerName}
                        </h4>

                        <div class="text-muted">
                            ${offerTitle}
                        </div>

                    </div>


                    <div class="text-md-end">

                        <div class="display-6 fw-bold text-primary">
                            ${matchScore}
                        </div>

                        <div class="small text-muted">
                            Match Score
                        </div>

                    </div>

                </div>


                <hr>


                <!-- Main information -->

                <div class="row g-4">

                    <div class="col-lg-7">

                        <p class="text-muted mb-4">
                            ${description}
                        </p>


                        <div class="row g-3">

                            <div class="col-sm-6">

                                <div class="small text-muted">
                                    Price
                                </div>

                                <div class="fw-bold fs-5">
                                    ${price}
                                </div>

                            </div>


                            <div class="col-sm-6">

                                <div class="small text-muted">
                                    Availability
                                </div>

                                <div class="fw-semibold">
                                    ${deliveryTime}
                                </div>

                            </div>


                            <div class="col-sm-6">

                                <div class="small text-muted">
                                    Location
                                </div>

                                <div class="fw-semibold">
                                    ${location}
                                </div>

                            </div>


                            <div class="col-sm-6">

                                <div class="small text-muted">
                                    Provider Rating
                                </div>

                                <div class="fw-semibold">
                                    ★ ${Number(
                                        provider.rating || 0
                                    ).toFixed(1)}
                                </div>

                            </div>

                        </div>


                        <!-- Negotiation action -->

                        <div class="mt-4">
                            ${negotiationButton}
                        </div>

                    </div>


                    <!-- Score breakdown -->

                    <div class="col-lg-5">

                        <div class="bg-light rounded-4 p-3">

                            <h6 class="fw-bold mb-3">
                                Why this match?
                            </h6>

                            <div class="small text-muted mb-3">
                                ${reason}
                            </div>


                            <div class="d-flex
                                        justify-content-between
                                        small mb-1">

                                <span>Trust</span>

                                <strong>
                                    ${trustScore}/100
                                </strong>

                            </div>

                            <div
                                class="progress mb-3"
                                style="height: 6px;"
                            >
                                <div
                                    class="progress-bar"
                                    style="width: ${Math.min(
                                        Number(trustScore),
                                        100
                                    )}%;"
                                ></div>
                            </div>


                            <div class="d-flex
                                        justify-content-between
                                        small mb-1">

                                <span>Risk</span>

                                <strong>
                                    ${riskScore}/100
                                </strong>

                            </div>

                            <div
                                class="progress"
                                style="height: 6px;"
                            >
                                <div
                                    class="progress-bar"
                                    style="width: ${Math.min(
                                        Number(riskScore),
                                        100
                                    )}%;"
                                ></div>
                            </div>

                            ${alertsHtml}

                        </div>

                    </div>

                </div>

            </div>

        </div>
    `;
}


/* =========================================================
   MATCH RESULTS
   ========================================================= */

function renderResults(data) {

    const resultsElement =
        getElement("serviceResults");

    if (!resultsElement) {
        return;
    }


    const matches =
        Array.isArray(data.matches)
            ? data.matches
            : [];


    let html = "";


    html += renderRequirement(
        data.requirement
    );


    if (matches.length === 0) {

        html += `
            <div class="alert alert-warning rounded-4">

                <strong>
                    No strong matches found.
                </strong>

                <div class="mt-1">
                    Try changing the budget, location,
                    service category or timing.
                </div>

            </div>
        `;

        resultsElement.innerHTML = html;

        return;
    }


    html += `
        <div class="d-flex justify-content-between
                    align-items-center mb-3">

            <div>

                <h4 class="fw-bold mb-1">
                    Best matches
                </h4>

                <div class="text-muted small">
                    ${matches.length}
                    option${matches.length === 1 ? "" : "s"}
                    found
                </div>

            </div>

        </div>
    `;


    matches.forEach(
        (match, index) => {
            html += renderMatch(
                match,
                index
            );
        }
    );


    resultsElement.innerHTML = html;
}


/* =========================================================
   API
   ========================================================= */

async function findServiceMatches(
    requirementText
) {

    const response = await fetch(
        "/service/match",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                requirement: requirementText
            })
        }
    );


    let data;

    try {
        data = await response.json();
    } catch (error) {
        throw new Error(
            "The server returned an invalid response."
        );
    }


    if (!response.ok || !data.success) {
        throw new Error(
            data.error ||
            "Unable to find service matches."
        );
    }


    return data;
}


/* =========================================================
   SERVICE FORM
   ========================================================= */

async function handleServiceSubmit(event) {

    event.preventDefault();


    const requirementElement =
        getElement("requirement");

    const resultsElement =
        getElement("serviceResults");


    if (!requirementElement) {
        return;
    }


    const requirementText =
        requirementElement.value.trim();


    if (!requirementText) {

        showStatus(
            "Please describe what service you need.",
            "warning"
        );

        requirementElement.focus();

        return;
    }


    setLoading(true);
    hideStatus();


    if (resultsElement) {
        resultsElement.innerHTML = "";
    }


    showStatus(
        "Understanding your requirement and comparing available providers...",
        "info"
    );


    try {

        const data =
            await findServiceMatches(
                requirementText
            );


        showStatus(
            "Best matches found successfully.",
            "success"
        );


        renderResults(data);


        if (resultsElement) {

            resultsElement.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }

    } catch (error) {

        console.error(
            "BESTORA FIT service matching error:",
            error
        );


        showStatus(
            error.message ||
            "Something went wrong while finding matches.",
            "error"
        );

    } finally {

        setLoading(false);

    }
}


/* =========================================================
   NAVIGATION
   ========================================================= */

function initializeSmoothScrolling() {

    const links =
        document.querySelectorAll(
            'a[href^="#"]'
        );


    links.forEach((link) => {

        link.addEventListener(
            "click",
            (event) => {

                const targetId =
                    link.getAttribute("href");


                if (
                    !targetId ||
                    targetId === "#"
                ) {
                    return;
                }


                const target =
                    document.querySelector(
                        targetId
                    );


                if (!target) {
                    return;
                }


                event.preventDefault();


                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }
        );

    });
}


/* =========================================================
   INITIALIZATION
   ========================================================= */

function initializeApp() {

    const serviceForm =
        getElement("serviceForm");


    if (serviceForm) {

        serviceForm.addEventListener(
            "submit",
            handleServiceSubmit
        );

    }


    initializeSmoothScrolling();


    console.log(
        "BESTORA FIT frontend initialized."
    );
}


/* =========================================================
   START
   ========================================================= */

if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initializeApp
    );

} else {

    initializeApp();

} 