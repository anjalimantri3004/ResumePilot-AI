// ResumePilot AI - Universal Job Description Capture (Final)

const captureBtn = document.getElementById("captureBtn");
const openBtn = document.getElementById("openAppBtn");
const status = document.getElementById("status");

// ----------------------------------------------------
// Capture Job Description
// ----------------------------------------------------

captureBtn.addEventListener("click", async () => {

    status.textContent = "Scanning page...";

    try {

        const [tab] = await chrome.tabs.query({
            active: true,
            currentWindow: true
        });

        const [{ result }] = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: extractJobDescriptionUniversal
        });

        if (!result || result.length < 250) {
            status.textContent = "No Job Description found.";
            return;
        }

        // Copy JD
        await navigator.clipboard.writeText(result);

        // Success UI
        captureBtn.textContent = "✓ Captured";
        captureBtn.style.background = "#16a34a";

        status.textContent =
            `Copied ${result.length.toLocaleString()} characters. Opening ResumePilot...`;

        // Auto-open ResumePilot
        chrome.tabs.create({
            url: "http://localhost:8501"
        });

        // Reset button after 2 sec
        setTimeout(() => {
            captureBtn.textContent = "Capture Job Description";
            captureBtn.style.background = "#2563eb";
        }, 2000);

    } catch (err) {

        console.error(err);
        status.textContent = "Capture failed.";

    }

});

// ----------------------------------------------------
// Manual Open ResumePilot
// ----------------------------------------------------

openBtn.addEventListener("click", () => {

    chrome.tabs.create({
        url: "http://localhost:8501"
    });

});

// ----------------------------------------------------
// Smart Universal JD Extraction
// ----------------------------------------------------

function extractJobDescriptionUniversal() {

    const pageText = document.body.innerText
        .replace(/\n{3,}/g, "\n\n")
        .replace(/[ \t]{2,}/g, " ")
        .trim();

    // JD usually starts from these
    const startKeywords = [
        "Job Description",
        "ABOUT THE ROLE",
        "About the Role",
        "ROLE OVERVIEW",
        "Responsibilities",
        "Key Responsibilities"
    ];

    // Stop before these sections
    const endKeywords = [
        "About Company",
        "About Us",
        "Similar Jobs",
        "Share this job",
        "Share Job",
        "Job Insights",
        "Powered By",
        "Candidate Login",
        "View All",
        "Related Jobs",
        "Other Jobs"
    ];

    let start = -1;

    for (const key of startKeywords) {
        const idx = pageText.indexOf(key);
        if (idx !== -1 && (start === -1 || idx < start)) {
            start = idx;
        }
    }

    // Fallback: look for Requirements/Qualifications
    if (start === -1) {
        const fallback = [
            "Requirements",
            "Qualifications",
            "Must Have",
            "What You'll Do"
        ];

        for (const key of fallback) {
            const idx = pageText.indexOf(key);
            if (idx !== -1 && (start === -1 || idx < start)) {
                start = idx;
            }
        }
    }

    if (start === -1) {
        start = 0;
    }

    let jd = pageText.substring(start);

    let end = jd.length;

    for (const key of endKeywords) {
        const idx = jd.indexOf(key);
        if (idx !== -1 && idx < end) {
            end = idx;
        }
    }

    jd = jd.substring(0, end);

    return jd
        .replace(/[ \t]{2,}/g, " ")
        .replace(/\n{3,}/g, "\n\n")
        .trim();
}