(function () {

    "use strict";

    const STORAGE_KEYS = {
        results: "bestora_product_results",
        requirement: "bestora_product_requirement",
        selectedProduct: "bestora_selected_product"
    };

    const ROUTES = {
        match: "/product/match",
        deal: "/product/deal",
        analyzing: "/product/analyzing",
        results: "/product/results",
        requirement: "/product/"
    };


    // =========================================================
    // HELPERS
    // =========================================================

    function getElement(id) {
        return document.getElementById(id);
    }


    function showElement(element) {
        if (element) {
            element.classList.remove("d-none");
        }
    }


    function hideElement(element) {
        if (element) {
            element.classList.add("d-none");
        }
    }


    function setText(id, value) {
        const element = getElement(id);

        if (element) {
            element.textContent = value;
        }
    }


    function formatCurrency(value) {

        if (
            value === null ||
            value === undefined ||
            value === ""
        ) {
            return "Price unavailable";
        }

        const numericValue = Number(value);

        if (Number.isNaN(numericValue)) {
            return String(value);
        }

        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }).format(numericValue);
    }


    function escapeHtml(value) {

        const div = document.createElement("div");

        div.textContent = value ?? "";

        return div.innerHTML;
    }


    function getStoredJson(key) {

        try {

            const value =
                sessionStorage.getItem(key);

            if (!value) {
                return null;
            }

            return JSON.parse(value);

        } catch (error) {

            console.error(
                "Unable to read stored product data:",
                error
            );

            return null;
        }
    }


    function setStoredJson(key, value) {

        sessionStorage.setItem(
            key,
            JSON.stringify(value)
        );
    }


    // =========================================================
    // REQUIREMENT PAGE
    // =========================================================

    function initializeRequirementPage() {

        const form =
            getElement("productRequirementForm");

        if (!form) {
            return;
        }

        const textarea =
            getElement("productRequirement");

        const errorElement =
            getElement("productRequirementError");

        const processingElement =
            getElement("productProcessing");

        const submitButton =
            getElement("findProductButton");

        const exampleButtons =
            document.querySelectorAll(
                ".product-example"
            );


        exampleButtons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        if (textarea) {

                            textarea.value =
                                button.dataset.requirement ||
                                "";

                            textarea.focus();
                        }
                    }
                );
            }
        );


        form.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();

                const requirement =
                    (
                        textarea?.value ||
                        ""
                    ).trim();


                hideElement(errorElement);


                if (!requirement) {

                    if (errorElement) {

                        errorElement.textContent =
                            "Please describe what product you need.";

                        showElement(errorElement);
                    }

                    return;
                }


                showElement(processingElement);


                if (submitButton) {

                    submitButton.disabled = true;

                    submitButton.textContent =
                        "Analyzing...";
                }


                try {

                    /*
                     * Product Mode currently sends the
                     * natural-language requirement as the query.
                     */

                    const response =
                        await fetch(
                            ROUTES.match,
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    query: requirement,
                                    limit: 10
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
                            "Unable to find matching products."
                        );
                    }


                    setStoredJson(
                        STORAGE_KEYS.requirement,
                        {
                            original_text:
                                requirement,

                            ...data.requirement
                        }
                    );


                    setStoredJson(
                        STORAGE_KEYS.results,
                        data
                    );


                    window.location.href =
                        ROUTES.results;


                } catch (error) {

                    console.error(
                        "Product matching failed:",
                        error
                    );


                    if (errorElement) {

                        errorElement.textContent =
                            error.message ||
                            "Unable to process your product request.";

                        showElement(errorElement);
                    }


                    hideElement(
                        processingElement
                    );


                    if (submitButton) {

                        submitButton.disabled =
                            false;

                        submitButton.textContent =
                            "Find Best Products";
                    }
                }
            }
        );
    }


    // =========================================================
    // ANALYZING PAGE
    // =========================================================

    function initializeAnalyzingPage() {

        const progressBar =
            getElement(
                "productAnalysisProgressBar"
            );

        const percentage =
            getElement(
                "productAnalysisPercent"
            );

        const requirement =
            getStoredJson(
                STORAGE_KEYS.requirement
            );


        if (!progressBar) {
            return;
        }


        if (requirement) {

            setText(
                "productAnalyzingRequirement",
                requirement.original_text ||
                "Your requirement"
            );
        }


        const steps = [
            "productAnalysisStep1",
            "productAnalysisStep2",
            "productAnalysisStep3",
            "productAnalysisStep4"
        ];


        let currentStep = 0;


        function updateProgress() {

            currentStep += 1;


            const value =
                Math.min(
                    currentStep * 25,
                    100
                );


            progressBar.style.width =
                value + "%";


            progressBar.setAttribute(
                "aria-valuenow",
                String(value)
            );


            if (percentage) {

                percentage.textContent =
                    value + "%";
            }


            if (currentStep > 0) {

                const previousStep =
                    getElement(
                        steps[currentStep - 1]
                    );


                if (previousStep) {

                    const badge =
                        previousStep.querySelector(
                            ".badge"
                        );


                    if (badge) {

                        badge.classList.remove(
                            "bg-secondary"
                        );

                        badge.classList.add(
                            "bg-success"
                        );

                        badge.textContent =
                            "✓";
                    }
                }
            }


            if (
                currentStep <
                steps.length
            ) {

                window.setTimeout(
                    updateProgress,
                    500
                );

                return;
            }


            window.setTimeout(
                function () {

                    window.location.href =
                        ROUTES.results;

                },
                400
            );
        }


        updateProgress();
    }


    // =========================================================
    // RESULTS PAGE
    // =========================================================

    function initializeResultsPage() {

        const resultsContainer =
            getElement(
                "productResultsList"
            );


        if (!resultsContainer) {
            return;
        }


        const storedResults =
            getStoredJson(
                STORAGE_KEYS.results
            );


        const requirement =
            getStoredJson(
                STORAGE_KEYS.requirement
            );


        if (!storedResults) {

            showElement(
                getElement(
                    "productNoResults"
                )
            );

            return;
        }


        renderRequirementSummary(
            requirement,
            storedResults
        );


        const matches =
            Array.isArray(
                storedResults.matches
            )
                ? storedResults.matches
                : [];


        setText(
            "productResultCount",
            String(matches.length)
        );


        if (matches.length === 0) {

            showElement(
                getElement(
                    "productNoResults"
                )
            );

            return;
        }


        resultsContainer.innerHTML = "";


        matches.forEach(
            function (match) {

                const card =
                    createProductCard(match);

                resultsContainer.appendChild(
                    card
                );
            }
        );
    }


    function renderRequirementSummary(
        requirement,
        results
    ) {

        const text =
            requirement?.original_text ||
            results?.requirement?.original_text ||
            results?.requirement?.query ||
            "Your product requirement";


        setText(
            "productRequirementSummary",
            text
        );


        if (
            requirement?.category ||
            results?.requirement?.category
        ) {

            setText(
                "productCategory",
                requirement?.category ||
                results?.requirement?.category ||
                "Product"
            );
        }


        if (
            requirement?.budget_max !== undefined ||
            results?.requirement?.budget_max !== undefined
        ) {

            const budget =
                requirement?.budget_max ??
                results?.requirement?.budget_max;


            setText(
                "productBudget",
                formatCurrency(budget)
            );
        }
    }


    function createProductCard(match) {

        const product =
            match.product || {};


        const cardWrapper =
            document.createElement("div");


        cardWrapper.className =
            "col-12 col-md-6 col-lg-4";


        const name =
            escapeHtml(
                product.name ||
                "Unnamed Product"
            );


        const brand =
            escapeHtml(
                product.brand ||
                ""
            );


        const description =
            escapeHtml(
                product.description ||
                "No description available."
            );


        const price =
            formatCurrency(
                product.price
            );


        const rating =
            Number(
                product.rating || 0
            );


        const matchScore =
            Number(
                match.match_score ||
                match.score ||
                0
            );


        const dealScore =
            Number(
                match.deal_score ||
                0
            );


        const reason =
            escapeHtml(
                match.recommendation_reason ||
                match.reason ||
                "This product matches your requirement."
            );


        cardWrapper.innerHTML = `

            <div class="card h-100 border-0 shadow-sm rounded-4">

                <div class="card-body p-4">

                    <div class="mb-3">

                        <h5 class="fw-bold mb-1">
                            ${name}
                        </h5>

                        ${
                            brand
                                ? `
                                    <div class="text-muted small">
                                        ${brand}
                                    </div>
                                `
                                : ""
                        }

                    </div>


                    <p class="text-muted small">
                        ${description}
                    </p>


                    <div
                        class="d-flex justify-content-between align-items-center mb-3"
                    >

                        <span class="h4 fw-bold mb-0">
                            ${price}
                        </span>

                        <span class="text-muted small">
                            ⭐ ${rating.toFixed(1)}
                        </span>

                    </div>


                    <div class="row g-2 mb-3">

                        <div class="col-6">

                            <div
                                class="bg-light rounded p-2 text-center"
                            >

                                <div class="small text-muted">
                                    Match
                                </div>

                                <strong>
                                    ${matchScore.toFixed(0)}%
                                </strong>

                            </div>

                        </div>


                        <div class="col-6">

                            <div
                                class="bg-light rounded p-2 text-center"
                            >

                                <div class="small text-muted">
                                    Deal
                                </div>

                                <strong>

                                    ${
                                        dealScore > 0
                                            ? dealScore.toFixed(0) + "%"
                                            : "Evaluating"
                                    }

                                </strong>

                            </div>

                        </div>

                    </div>


                    <div class="small mb-3">

                        <strong>
                            Why this product?
                        </strong>


                        <div class="text-muted mt-1">
                            ${reason}
                        </div>

                    </div>


                    <button
                        type="button"
                        class="btn btn-primary w-100 product-deal-button"
                    >
                        Check Best Deal
                    </button>

                </div>

            </div>
        `;


        const dealButton =
            cardWrapper.querySelector(
                ".product-deal-button"
            );


        if (dealButton) {

            dealButton.addEventListener(
                "click",
                function () {

                    evaluateDeal(
                        match,
                        dealButton
                    );
                }
            );
        }


        return cardWrapper;
    }


    // =========================================================
    // DEAL OPTIMIZATION
    // =========================================================

    async function evaluateDeal(
        match,
        button
    ) {

        const product =
            match.product || {};


        const requirement =
            getStoredJson(
                STORAGE_KEYS.requirement
            );


        const originalText =
            button.textContent;


        button.disabled = true;

        button.textContent =
            "Checking...";


        try {

            const response =
                await fetch(
                    ROUTES.deal,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({

                            product:
                                product,

                            budget_max:
                                requirement?.budget_max ??
                                null
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
                    "Unable to evaluate this deal."
                );
            }


            const deal =
                data.deal || {};


            match.deal_score =
                deal.deal_score;


            setStoredJson(
                STORAGE_KEYS.selectedProduct,
                {
                    match: match,
                    deal: deal
                }
            );


            // FIXED:
            // Pass the actual button and deal object.
            showDealResult(
                button,
                deal
            );


        } catch (error) {

            console.error(
                "Deal optimization failed:",
                error
            );


            button.textContent =
                "Deal check failed";


            window.setTimeout(
                function () {

                    button.textContent =
                        originalText;

                    button.disabled =
                        false;

                },
                1500
            );
        }
    }


    // =========================================================
    // SHOW DEAL RESULT
    // =========================================================

    function showDealResult(
        button,
        deal
    ) {

        const card =
            button.closest(
                ".card"
            );


        if (!card) {
            return;
        }


        let dealBox =
            card.querySelector(
                ".product-deal-result"
            );


        if (!dealBox) {

            dealBox =
                document.createElement(
                    "div"
                );


            dealBox.className =
                "product-deal-result alert alert-success mt-3 mb-0";


            button.parentElement.appendChild(
                dealBox
            );
        }


        const score =
            Number(
                deal.deal_score || 0
            );


        const product =
            getStoredJson(
                STORAGE_KEYS.selectedProduct
            )?.match?.product || {};


        const originalPrice =
            Number(
                product.price || 0
            );


        const dealPrice =
            Number(
                deal.optimized_price ??
                deal.final_price ??
                deal.recommended_price ??
                deal.target_price ??
                originalPrice
            );


        const savings =
            Math.max(
                originalPrice -
                dealPrice,
                0
            );


        const savingsPercent =
            originalPrice > 0
                ? (
                    savings /
                    originalPrice
                ) * 100
                : 0;


        dealBox.innerHTML = `

            <div class="mb-3">

                <strong>

                    ${escapeHtml(
                        deal.deal_level ||
                        "DEAL"
                    )}

                    —
                    ${score.toFixed(0)}%
                    Deal Score

                </strong>


                <div class="small mt-1">

                    ${escapeHtml(
                        deal.deal_reason ||
                        "This product offers good overall value."
                    )}

                </div>

            </div>


            <div
                class="bg-white rounded-3 p-3 mb-3"
                style="
                    border: 1px solid rgba(0,0,0,0.08);
                "
            >

                <div
                    class="d-flex justify-content-between mb-2"
                >

                    <span class="text-muted">
                        Original Price
                    </span>

                    <strong>
                        ${formatCurrency(
                            originalPrice
                        )}
                    </strong>

                </div>


                <div
                    class="d-flex justify-content-between mb-2"
                >

                    <span class="text-success">
                        Best Deal Price
                    </span>

                    <strong class="text-success">

                        ${formatCurrency(
                            dealPrice
                        )}

                    </strong>

                </div>


                <div
                    class="d-flex justify-content-between"
                >

                    <span class="text-success">
                        You Save
                    </span>

                    <strong class="text-success">

                        ${formatCurrency(
                            savings
                        )}

                        (${savingsPercent.toFixed(0)}%)

                    </strong>

                </div>

            </div>


            <button
                type="button"
                class="btn btn-primary w-100 rounded-3 fw-semibold product-buy-button"
            >
                Proceed to Buy
            </button>
        `;


        button.textContent =
            "Deal Evaluated";


        button.disabled = true;


        const buyButton =
            dealBox.querySelector(
                ".product-buy-button"
            );


        if (buyButton) {

            buyButton.addEventListener(
                "click",
                function () {

                    const selectedProduct =
                        getStoredJson(
                            STORAGE_KEYS.selectedProduct
                        ) || {};


                    const selectedMatch =
                        selectedProduct.match ||
                        {};


                    const selectedProductData =
                        selectedMatch.product ||
                        product;


                    const params =
                        new URLSearchParams({

                            product_name:
                                selectedProductData.name ||
                                "Selected Product",

                            seller_name:
                                selectedProductData.seller ||
                                "Selected Seller",

                            original_price:
                                String(
                                    Number(
                                        selectedProductData.price ||
                                        0
                                    )
                                ),

                            deal_price:
                                String(
                                    dealPrice
                                ),

                            savings:
                                String(
                                    savings
                                ),

                            savings_percent:
                                savingsPercent.toFixed(0)
                        });


                    window.location.href =
                        `/product/billing?${params.toString()}`;
                }
            );
        }
    }


    // =========================================================
    // INITIALIZATION
    // =========================================================

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            initializeRequirementPage();

            initializeAnalyzingPage();

            initializeResultsPage();

        }
    );

})(); 