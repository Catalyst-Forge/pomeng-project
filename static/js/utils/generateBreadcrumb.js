// Breadcrumb Link Generate Function
export const generateBreadcrumb = (currentPage) => {
  const breadcrumbContainer = document.getElementById("breadcrumb");
  breadcrumbContainer.innerHTML = ""; // Clear existing items

  // Get path segments and start building HTML
  const pathSegments = currentPage.split("/").filter(Boolean);
  let accumulatedPath = "";

  // Loop through segments and add to breadcrumb
  pathSegments.forEach((segment, index) => {
    accumulatedPath += `/${segment}`;
    const isLastSegment = index === pathSegments.length - 1;
    const segmentName = segment.replace(/-/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());

    // Set last segment as active
    breadcrumbContainer.innerHTML += isLastSegment
      ? `<li class="breadcrumb-item active fw-bold" aria-current="page">${segmentName}</li>`
      : `<li class="breadcrumb-item"><a href="${accumulatedPath}" class="link-info text-decoration-none breadcrumb-link">${segmentName}</a></li>`;
  });
};
