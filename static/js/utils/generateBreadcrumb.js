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

    // Format segment name (capitalize and replace dashes with spaces)
    const segmentName = segment.replace(/-/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());

    // Check if segment is numeric (assume it's an ID)
    const isIdSegment = /^\d+$/.test(segment);

    // Set last segment as active or disable numeric segments
    if (isLastSegment) {
      breadcrumbContainer.innerHTML += `<li class="breadcrumb-item active fw-bold" aria-current="page">${segmentName}</li>`;
    } else if (isIdSegment) {
      breadcrumbContainer.innerHTML += `<li class="breadcrumb-item"><span class="text-body-secondary breadcrumb-link">${segmentName}</span></li>`;
    } else {
      breadcrumbContainer.innerHTML += `<li class="breadcrumb-item"><a href="${accumulatedPath}" class="link-info text-decoration-none breadcrumb-link">${segmentName}</a></li>`;
    }
  });
};
