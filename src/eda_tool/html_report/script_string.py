script_string =  """
    <script>

document.addEventListener("click", function(e) {
    if (!e.target.classList.contains("tab-button")) return;

    const tabId = e.target.dataset.tab;

    // Scope = the nearest .tabs container
    const tabsContainer = e.target.closest(".tabs");

    // Deactivate only buttons inside this tabs container
    tabsContainer.querySelectorAll(".tab-button").forEach(btn => {
        btn.classList.remove("active");
    });

    // Activate clicked button
    e.target.classList.add("active");

    // Find the parent section-box that contains the content blocks
    const sectionBox = tabsContainer.closest(".section-box");

    // Deactivate only content blocks inside this section-box
    sectionBox.querySelectorAll(".tab-content").forEach(cnt => {
        cnt.classList.remove("active");
    });

    // Activate the matching content
    const content = sectionBox.querySelector("#" + tabId);
    if (content) content.classList.add("active");
});


document.addEventListener("DOMContentLoaded", function() {
    // Top-level interactions tabs (col1)
    const interactionsBox = document.querySelector(".interactions-box");
    if (!interactionsBox) return;

    const topButtons = interactionsBox.querySelectorAll(".interactions-tab-button");
    const topContents = interactionsBox.querySelectorAll(".interactions-tab-content");

    topButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.dataset.interactionsTab;

            // deactivate all top-level
            topButtons.forEach(b => b.classList.remove("interactions-tab-button-active"));
            topContents.forEach(c => c.classList.remove("interactions-tab-content-active"));

            // activate clicked
            btn.classList.add("interactions-tab-button-active");
            const targetContent = interactionsBox.querySelector("#" + targetId);
            if (targetContent) {
                targetContent.classList.add("interactions-tab-content-active");

                // inside this content, activate FIRST nested subtab by default
                const nestedButtons = targetContent.querySelectorAll(".interactions-subtab-button");
                const nestedContents = targetContent.querySelectorAll(".interactions-subtab-content");

                nestedButtons.forEach(b => b.classList.remove("interactions-subtab-button-active"));
                nestedContents.forEach(c => c.classList.remove("interactions-subtab-content-active"));

                if (nestedButtons.length > 0 && nestedContents.length > 0) {
                    nestedButtons[0].classList.add("interactions-subtab-button-active");
                    nestedContents[0].classList.add("interactions-subtab-content-active");
                }
            }
        });
    });

    // Nested interactions subtabs (col2)
    interactionsBox.querySelectorAll(".interactions-tab-content").forEach(topContent => {
        const nestedButtons = topContent.querySelectorAll(".interactions-subtab-button");
        const nestedContents = topContent.querySelectorAll(".interactions-subtab-content");

        nestedButtons.forEach(btn => {
            btn.addEventListener("click", () => {
                const targetId = btn.dataset.interactionsSubtab;

                nestedButtons.forEach(b => b.classList.remove("interactions-subtab-button-active"));
                nestedContents.forEach(c => c.classList.remove("interactions-subtab-content-active"));

                btn.classList.add("interactions-subtab-button-active");
                const targetContent = topContent.querySelector("#" + targetId);
                if (targetContent) {
                    targetContent.classList.add("interactions-subtab-content-active");
                }
            });
        });
    });
});

document.addEventListener("click", function(e) {
    if (e.target.classList.contains("more-details-btn")) {
        const panelId = e.target.getAttribute("data-target");
        const panel = document.getElementById(panelId);

        // Toggle panel visibility
        const isOpen = panel.classList.toggle("open");

        // Update button text
        e.target.textContent = isOpen ? "Less details" : "More details";
    }
});

// Tab system that works for nested panels
document.addEventListener("click", function(e) {
    if (!e.target.classList.contains("tab-button")) return;

    const tabId = e.target.getAttribute("data-tab");

    // Scope: find nearest container that holds tab-content
    const container = e.target.closest(".details-panel") || 
                      e.target.closest(".section-box");

    // Deactivate all tabs in this container
    container.querySelectorAll(".tab-button").forEach(btn => {
        btn.classList.remove("active");
    });
    container.querySelectorAll(".tab-content").forEach(tab => {
        tab.classList.remove("active");
    });

    // Activate clicked tab + its content
    e.target.classList.add("active");
    container.querySelector("#" + tabId).classList.add("active");
});

// Inner tab system (Extreme Values)
document.addEventListener("click", function(e) {
    if (!e.target.classList.contains("inner-tab-button")) return;

    const tabId = e.target.getAttribute("data-inner-tab");
    if (!tabId) return;

    // Scope: nearest inner-tabs container
    const tabsContainer = e.target.closest(".inner-tabs");
    if (!tabsContainer) return;

    // Content scope: parent that holds inner-tabs + inner-tab-content
    const contentScope = tabsContainer.parentElement;

    // Deactivate all inner buttons in this group
    tabsContainer.querySelectorAll(".inner-tab-button").forEach(btn => {
        btn.classList.remove("active");
    });

    // Deactivate all inner contents in this scope
    contentScope.querySelectorAll(".inner-tab-content").forEach(tab => {
        tab.classList.remove("active");
    });

    // Activate clicked button
    e.target.classList.add("active");

    // Activate matching content
    const targetContent = contentScope.querySelector("#" + tabId);
    if (targetContent) {
        targetContent.classList.add("active");
    }
});


</script>"""