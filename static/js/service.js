/**
 * BESTORA FIT
 * Service Mode Frontend Controller
 *
 * Handles:
 * 1. Service requirement submission
 * 2. Requirement analysis state
 * 3. Match results
 * 4. Provider detail view
 * 5. Navigation to negotiation
 */


/* =========================================================
   GLOBAL HELPERS
   ========================================================= */

function getElement(id) {
    return document.getElementById(id);
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


function formatNumber(value) {
    const number = Number(value || 0);

    return number.toLocaleString("en-IN");
}


function getRiskClass(level) {
    const risk = String(level || "LOW").toUpperCase();

    if (risk === "CRITICAL" || risk === "HIGH") {
        return "text-bg-danger";
    }

    if (risk === "MEDIUM") {
        return "text-bg-warning";
    }

    return "text-bg-success";
}


function getTrustClass(level) {
    const trust = String(level || "").toLowerCase();

    if (trust === "excellent") {
        return "text-bg-success";
    }

    if (trust === "good") {
        return "text-bg-primary";
    }

    if (trust === "average") {
        return "text-bg-warning";
    }

    return "text-bg-secondary";
}


function encodeParameter(value) {
    return encodeURIComponent(
        value === null || value === undefined
            ? ""
            : String(value)
    );
}


/* =========================================================
   API
   ========================================================= */

async function postServiceRequirement(requirement) {

    const response = await fetch(
        "/service/match",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                requirement: requirement
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
            "Unable to process the service requirement."
        );
    }


    return data;
}


/* =========================================================
   REQUIREMENT PAGE
   ========================================================= */

function initializeRequirementPage() {

    const form =
        getElement("serviceRequirementForm");

    const textarea =
        getElement("serviceRequirement");

    const button =
        getElement("findServiceButton");

    const processing =
        getElement("serviceProcessing");

    const errorElement =
        getElement("serviceRequirementError");


    if (!form || !textarea) {
        return;
    }


    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const requirement =
                textarea.value.trim();


            if (!requirement) {

                showRequirementError(
                    "Please describe the service you need."
                );

                textarea.focus();

                return;
            }


            clearRequirementError();


            if (button) {
                button.disabled = true;
                button.textContent =
                    "Understanding Requirement...";
            }


            if (processing) {
                processing.hidden = false;
            }


            try {

                const data =
                    await postServiceRequirement(
                        requirement
                    );


                /*
                 * Store the complete response so the results
                 * page can render it without making another
                 * unnecessary request.
                 */

                sessionStorage.setItem(
                    "bestora_service_results",
                    JSON.stringify(data)
                );


                sessionStorage.setItem(
                    "bestora_service_requirement",
                    requirement
                );


                window.location.href =
                    "/service/results";

            } catch (error) {

                console.error(
                    "Service requirement error:",
                    error
                );


                showRequirementError(
                    error.message ||
                    "Unable to process your requirement."
                );


                if (processing) {
                    processing.hidden = true;
                }

            } finally {

                if (button) {
                    button.disabled = false;
                    button.textContent =
                        "Find Best Matches";
                }

            }

        }
    );
}


function showRequirementError(message) {

    const errorElement =
        getElement("serviceRequirementError");

    if (!errorElement) {
        return;
    }

    errorElement.textContent = message;
    errorElement.hidden = false;
}


function clearRequirementError() {

    const errorElement =
        getElement("serviceRequirementError");

    if (!errorElement) {
        return;
    }

    errorElement.textContent = "";
    errorElement.hidden = true;
}


/* =========================================================
   RESULTS PAGE
   ========================================================= */

function getStoredServiceResults() {

    const raw =
        sessionStorage.getItem(
            "bestora_service_results"
        );


    if (!raw) {
        return null;
    }


    try {
        return JSON.parse(raw);
    } catch (error) {

        console.error(
            "Invalid stored service results:",
            error
        );

        return null;
    }
}


function initializeResultsPage() {

    const resultsContainer =
        getElement("serviceResultsList");

    if (!resultsContainer) {
        return;
    }


    const data =
        getStoredServiceResults();


    if (!data || !data.success) {

        showNoResults();

        return;
    }


    renderRequirementSummary(
        data.requirement
    );


    const matches =
        Array.isArray(data.matches)
            ? data.matches
            : [];


    if (matches.length === 0) {

        showNoResults();

        return;
    }


    renderServiceMatches(
        matches
    );
}


function renderRequirementSummary(
    requirement
) {

    if (!requirement) {
        return;
    }


    const original =
        getElement("originalRequirement");

    const category =
        getElement("requirementCategory");

    const location =
        getElement("requirementLocation");

    const budget =
        getElement("requirementBudget");

    const urgency =
        getElement("requirementUrgency");


    if (original) {
        original.textContent =
            requirement.original_text ||
            "Requirement not available";
    }


    if (category) {
        category.textContent =
            requirement.category ||
            "Not specified";
    }


    if (location) {
        location.textContent =
            requirement.location ||
            "Not specified";
    }


    if (budget) {

        if (
            requirement.budget_max !== null &&
            requirement.budget_max !== undefined
        ) {

            budget.textContent =
                formatPrice(
                    requirement.budget_max
                );

        } else {

            budget.textContent =
                "Not specified";

        }

    }


    if (urgency) {
        urgency.textContent =
            requirement.urgency ||
            "Not specified";
    }
}


function renderServiceMatches(matches) {

    const container =
        getElement("serviceResultsList");

    if (!container) {
        return;
    }


    container.innerHTML = "";


    matches.forEach(
        function (match, index) {

            container.insertAdjacentHTML(
                "beforeend",
                createMatchCard(
                    match,
                    index
                )
            );

        }
    );
}


function createMatchCard(match, index) {

    const provider =
        match.provider || {};

    const offer =
        match.offer || {};


    const providerName =
        escapeHtml(
            provider.name ||
            "Unknown Provider"
        );


    const offerTitle =
        escapeHtml(
            offer.title ||
            "Service Offer"
        );


    const description =
        escapeHtml(
            offer.description ||
            provider.description ||
            "No description available."
        );


    const location =
        escapeHtml(
            provider.location ||
            "Location unavailable"
        );


    const deliveryTime =
        escapeHtml(
            offer.delivery_time ||
            "Not specified"
        );


    const trustLevel =
        escapeHtml(
            match.trust_level ||
            "Unknown"
        );


    const riskLevel =
        escapeHtml(
            match.risk_level ||
            "LOW"
        );


    const matchScore =
        Number(
            match.match_score || 0
        ).toFixed(1);


    const trustScore =
        Number(
            match.trust_score || 0
        ).toFixed(1);


    const riskScore =
        Number(
            match.risk_score || 0
        ).toFixed(0);


    const rating =
        Number(
            provider.rating || 0
        ).toFixed(1);


    const price =
        formatPrice(
            offer.price,
            offer.currency || "INR"
        );


    const trustClass =
        getTrustClass(
            match.trust_level
        );


    const riskClass =
        getRiskClass(
            match.risk_level
        );


    const reason =
        escapeHtml(
            match.recommendation_reason ||
            "Good overall match."
        );


    const riskAlerts =
        Array.isArray(match.risk_alerts)
            ? match.risk_alerts
            : [];


    const providerPayload = encodeParameter(
        JSON.stringify({
            provider: provider,
            offer: offer,
            match: match
        })
    );


    const riskAlertsHtml =
        riskAlerts.length > 0
            ? `
                <div class="mt-3">

                    <div class="small fw-semibold mb-2">
                        Risk alerts
                    </div>

                    ${riskAlerts
                        .slice(0, 3)
                        .map(
                            function (alert) {

                                return `
                                    <div
                                        class="small text-muted mb-1"
                                    >
                                        • ${escapeHtml(
                                            alert.message ||
                                            "Risk indicator detected."
                                        )}
                                    </div>
                                `;

                            }
                        )
                        .join("")
                    }

                </div>
            `
            : "";


    return `
        <div
            class="card border-0 shadow-sm rounded-4 mb-4
                   service-match-card"
        >

            <div class="card-body p-4 p-md-5">

                <!-- Header -->

                <div
                    class="d-flex
                           flex-column
                           flex-md-row
                           justify-content-between
                           gap-3"
                >

                    <div>

                        <div
                            class="d-flex
                                   flex-wrap
                                   align-items-center
                                   gap-2
                                   mb-2"
                        >

                            <span class="badge text-bg-dark">
                                #${index + 1}
                            </span>

                            <span
                                class="badge ${trustClass}"
                            >
                                ${trustLevel} Trust
                            </span>

                            <span
                                class="badge ${riskClass}"
                            >
                                ${riskLevel} Risk
                            </span>

                        </div>


                        <h3 class="fw-bold mb-1">
                            ${providerName}
                        </h3>


                        <div class="text-muted">
                            ${offerTitle}
                        </div>

                    </div>


                    <div class="text-md-end">

                        <div
                            class="display-6
                                   fw-bold
                                   text-primary"
                        >
                            ${matchScore}
                        </div>

                        <div class="small text-muted">
                            Match Score
                        </div>

                    </div>

                </div>


                <hr>


                <!-- Content -->

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

                                <div
                                    class="fw-bold fs-5"
                                >
                                    ${price}
                                </div>

                            </div>


                            <div class="col-sm-6">

                                <div class="small text-muted">
                                    Provider Rating
                                </div>

                                <div class="fw-semibold">
                                    ★ ${rating}
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
                                    Availability
                                </div>

                                <div class="fw-semibold">
                                    ${deliveryTime}
                                </div>

                            </div>

                        </div>


                        <!-- Actions -->

                        <div
                            class="d-flex
                                   flex-wrap
                                   gap-2
                                   mt-4"
                        >

                            <button
                                type="button"
                                class="btn btn-outline-dark
                                       view-provider-button"
                                data-provider="${providerPayload}"
                            >
                                View Provider
                            </button>


                            ${
                                Number(offer.price || 0) > 0
                                    ? `
                                        <button
                                            type="button"
                                            class="btn btn-primary
                                                   negotiate-button"
                                            data-provider="${providerPayload}"
                                        >
                                            Negotiate Better Price
                                        </button>
                                    `
                                    : ""
                            }

                        </div>

                    </div>


                    <!-- Score breakdown -->

                    <div class="col-lg-5">

                        <div
                            class="bg-light
                                   rounded-4
                                   p-4"
                        >

                            <h6 class="fw-bold mb-3">
                                Why this match?
                            </h6>


                            <p class="small text-muted mb-4">
                                ${reason}
                            </p>


                            <!-- Trust -->

                            <div
                                class="d-flex
                                       justify-content-between
                                       small mb-1"
                            >

                                <span>
                                    Trust
                                </span>

                                <strong>
                                    ${trustScore}/100
                                </strong>

                            </div>


                            <div
                                class="progress mb-3"
                                style="height: 7px;"
                            >

                                <div
                                    class="progress-bar"
                                    style="
                                        width: ${Math.min(
                                            Number(trustScore),
                                            100
                                        )}%;
                                    "
                                ></div>

                            </div>


                            <!-- Risk -->

                            <div
                                class="d-flex
                                       justify-content-between
                                       small mb-1"
                            >

                                <span>
                                    Risk
                                </span>

                                <strong>
                                    ${riskScore}/100
                                </strong>

                            </div>


                            <div
                                class="progress"
                                style="height: 7px;"
                            >

                                <div
                                    class="progress-bar"
                                    style="
                                        width: ${Math.min(
                                            Number(riskScore),
                                            100
                                        )}%;
                                    "
                                ></div>

                            </div>


                            ${riskAlertsHtml}

                        </div>

                    </div>

                </div>

            </div>

        </div>
    `;
}


/* =========================================================
   PROVIDER PAGE
   ========================================================= */

function initializeProviderPage() {

    const negotiateButton =
        getElement(
            "providerNegotiateButton"
        );


    if (!negotiateButton) {
        return;
    }


    const rawProvider =
        sessionStorage.getItem(
            "bestora_selected_provider"
        );


    if (!rawProvider) {

        showProviderError(
            "Provider information is unavailable. Please return to the results page."
        );

        negotiateButton.disabled = true;

        return;
    }


    let selected;


    try {

        selected =
            JSON.parse(rawProvider);

    } catch (error) {

        showProviderError(
            "Unable to load provider information."
        );

        negotiateButton.disabled = true;

        return;
    }


    renderProviderDetails(
        selected
    );


    negotiateButton.addEventListener(
        "click",
        function () {

            navigateToNegotiation(
                selected
            );

        }
    );
}


function renderProviderDetails(data) {

    const provider =
        data.provider || {};

    const offer =
        data.offer || {};

    const match =
        data.match || {};


    setText(
        "providerName",
        provider.name || "Provider"
    );


    setText(
        "providerCategory",
        provider.category || "Service Provider"
    );


    setText(
        "providerLocation",
        provider.location
            ? `📍 ${provider.location}`
            : "📍 Location unavailable"
    );


    setText(
        "providerMatchScore",
        Number(
            match.match_score || 0
        ).toFixed(1)
    );


    setText(
        "providerRating",
        `★ ${Number(
            provider.rating || 0
        ).toFixed(1)}`
    );


    setText(
        "providerReviews",
        formatNumber(
            provider.review_count
        )
    );


    setText(
        "providerJobs",
        formatNumber(
            provider.completed_jobs
        )
    );


    setText(
        "providerExperience",
        `${Number(
            provider.experience_years || 0
        )} years`
    );


    setText(
        "providerTrustScore",
        `${Number(
            match.trust_score || 0
        ).toFixed(1)}/100`
    );


    setText(
        "providerResponseRate",
        `${Number(
            provider.response_rate || 0
        ).toFixed(1)}%`
    );


    setProgress(
        "providerTrustProgress",
        match.trust_score
    );


    setProgress(
        "providerResponseProgress",
        provider.response_rate
    );


    setText(
        "offerTitle",
        offer.title || "Service Offer"
    );


    setText(
        "offerDescription",
        offer.description ||
        provider.description ||
        "No description available."
    );


    setText(
        "offerPrice",
        formatPrice(
            offer.price,
            offer.currency || "INR"
        )
    );


    setText(
        "offerCurrency",
        offer.currency || "INR"
    );


    setText(
        "offerAvailability",
        offer.availability || "Unknown"
    );


    setText(
        "offerDelivery",
        offer.delivery_time || "Not specified"
    );


    setText(
        "recommendationReason",
        match.recommendation_reason ||
        "This provider was selected based on your requirement."
    );


    setText(
        "providerRisk",
        `${String(
            match.risk_level || "LOW"
        ).toUpperCase()} RISK`
    );


    const verifiedElement =
        getElement("providerVerified");


    if (verifiedElement) {

        if (provider.verified) {

            verifiedElement.textContent =
                "✓ Verified";

            verifiedElement.className =
                "badge text-bg-success";

        } else {

            verifiedElement.textContent =
                "Unverified";

            verifiedElement.className =
                "badge text-bg-warning";

        }

    }


    const riskElement =
        getElement("providerRisk");


    if (riskElement) {

        riskElement.className =
            `badge ${getRiskClass(
                match.risk_level
            )}`;

    }


    renderProviderRiskAlerts(
        match.risk_alerts || []
    );
}


function setText(id, value) {

    const element =
        getElement(id);

    if (!element) {
        return;
    }

    element.textContent =
        value === null ||
        value === undefined
            ? ""
            : value;
}


function setProgress(id, value) {

    const element =
        getElement(id);

    if (!element) {
        return;
    }


    const percentage =
        Math.min(
            Math.max(
                Number(value || 0),
                0
            ),
            100
        );


    element.style.width =
        `${percentage}%`;

    element.setAttribute(
        "aria-valuenow",
        String(percentage)
    );
}


function renderProviderRiskAlerts(alerts) {

    const card =
        getElement("riskAlertsCard");

    const list =
        getElement("riskAlertsList");


    if (!card || !list) {
        return;
    }


    if (
        !Array.isArray(alerts) ||
        alerts.length === 0
    ) {

        card.hidden = true;
        list.innerHTML = "";

        return;
    }


    list.innerHTML =
        alerts
            .map(
                function (alert) {

                    return `
                        <div
                            class="border rounded-3
                                   p-3 mb-2"
                        >

                            <div
                                class="fw-semibold"
                            >
                                ${escapeHtml(
                                    alert.type ||
                                    "Risk Indicator"
                                )}
                            </div>

                            <div
                                class="small text-muted mt-1"
                            >
                                ${escapeHtml(
                                    alert.message ||
                                    "Risk indicator detected."
                                )}
                            </div>

                        </div>
                    `;

                }
            )
            .join("");


    card.hidden = false;
}


function showProviderError(message) {

    const element =
        getElement("providerError");

    if (!element) {
        return;
    }

    element.textContent =
        message;

    element.hidden = false;
}


/* =========================================================
   PROVIDER / NEGOTIATION NAVIGATION
   ========================================================= */

function openProviderDetails(payload) {

    sessionStorage.setItem(
        "bestora_selected_provider",
        JSON.stringify(payload)
    );


    window.location.href =
        "/service/provider";
}


function navigateToNegotiation(data) {

    const provider =
        data.provider || {};

    const offer =
        data.offer || {};

    const match =
        data.match || {};


    if (
        !offer.price ||
        Number(offer.price) <= 0
    ) {

        showProviderError(
            "Negotiation is unavailable because this offer has no valid price."
        );

        return;
    }


    const params =
        new URLSearchParams({
            provider_name:
                provider.name || "",

            offer_title:
                offer.title || "",

            original_price:
                String(offer.price),

            trust_score:
                String(match.trust_score || 0),

            match_score:
                String(match.match_score || 0),

            risk_level:
                String(match.risk_level || "LOW"),

            user_requirement:
                getStoredRequirementText()
        });


    window.location.href =
        `/negotiation/?${params.toString()}`;
}


function getStoredRequirementText() {

    return sessionStorage.getItem(
        "bestora_service_requirement"
    ) || "";
}


/* =========================================================
   RESULTS EVENTS
   ========================================================= */

function initializeResultsEvents() {

    const resultsContainer =
        getElement("serviceResultsList");


    if (!resultsContainer) {
        return;
    }


    resultsContainer.addEventListener(
        "click",
        function (event) {

            const providerButton =
                event.target.closest(
                    ".view-provider-button"
                );


            if (providerButton) {

                const encoded =
                    providerButton.dataset.provider;


                if (!encoded) {
                    return;
                }


                try {

                    const payload =
                        JSON.parse(
                            decodeURIComponent(
                                encoded
                            )
                        );


                    openProviderDetails(
                        payload
                    );

                } catch (error) {

                    console.error(
                        "Unable to open provider:",
                        error
                    );

                }

                return;
            }


            const negotiateButton =
                event.target.closest(
                    ".negotiate-button"
                );


            if (negotiateButton) {

                const encoded =
                    negotiateButton.dataset.provider;


                if (!encoded) {
                    return;
                }


                try {

                    const payload =
                        JSON.parse(
                            decodeURIComponent(
                                encoded
                            )
                        );


                    navigateToNegotiation(
                        payload
                    );

                } catch (error) {

                    console.error(
                        "Unable to open negotiation:",
                        error
                    );

                }

            }

        }
    );
}


/* =========================================================
   EMPTY RESULTS
   ========================================================= */

function showNoResults() {

    const results =
        getElement("serviceResultsList");

    const empty =
        getElement("noResults");


    if (results) {
        results.innerHTML = "";
    }


    if (empty) {
        empty.hidden = false;
    }
}


/* =========================================================
   GLOBAL INITIALIZATION
   ========================================================= */

function initializeServiceApp() {

    initializeRequirementPage();

    initializeResultsPage();

    initializeResultsEvents();

    initializeProviderPage();


    console.log(
        "BESTORA FIT Service Mode initialized."
    );
}


if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initializeServiceApp
    );

} else {

    initializeServiceApp();

} 