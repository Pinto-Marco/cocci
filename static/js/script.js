// Function to add product to cart
function addToCart(productCode, token) {
  fetch("/cart/add/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    body: JSON.stringify({
      product_code: productCode,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Update cart count in navbar
      const cartCountElement = document.getElementById("cart-count");
      if (cartCountElement) {
        const currentCount = parseInt(cartCountElement.textContent || "0");
        cartCountElement.textContent = currentCount + 1;
      }

      // Show feedback to user
      const notification = document.createElement("div");
      notification.className = "cart-notification";
      notification.textContent = "Product added to cart!";
      document.body.appendChild(notification);

      // Remove notification after 3 seconds
      setTimeout(() => {
        notification.style.opacity = "0";
        setTimeout(() => {
          document.body.removeChild(notification);
        }, 500);
      }, 2500);
    })
    .catch((error) => {
      console.error("Error adding to cart:", error);
    });
}

function removeFromCart(productCode, token) {
  fetch("/cart/remove/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    body: JSON.stringify({
      product_code: productCode,
      remove_all: true,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      window.location.reload();
    });
}

document.addEventListener("DOMContentLoaded", () => {
  const productCards = document.querySelectorAll(".product-card");

  productCards.forEach((card) => {
    const imgElement = card.querySelector(".product-card__image");
    // Retrieve the data-images attribute.
    // dataset.images automatically handles the 'data-' prefix.
    const imagesDataAttr = card.dataset.images;

    if (!imgElement || !imagesDataAttr) {
      // Skip if no image element or no images data
      return;
    }

    let imageUrls = [];
    try {
      // Parse the JSON string from data-images
      let parsedData = JSON.parse(imagesDataAttr);

      // Check if parsedData is an array and has items
      if (Array.isArray(parsedData) && parsedData.length > 0) {
        // Option 1: If data-images contains an array of base64 strings
        if (typeof parsedData[0] === "string") {
          imageUrls = parsedData.map(
            (base64) => `data:image/*;base64,${base64}`
          );
        }
        // Option 2: If data-images contains an array of objects like {image_base64: "..."}
        else if (
          typeof parsedData[0] === "object" &&
          parsedData[0].hasOwnProperty("image_base64")
        ) {
          imageUrls = parsedData.map(
            (obj) => `data:image/*;base64,${obj.image_base64}`
          );
        }
      }
    } catch (e) {
      console.error(
        "Failed to parse images data for product card. Ensure data-images contains valid JSON. Error:",
        e,
        "Data:",
        imagesDataAttr
      );
      return; // Skip this card if data is malformed
    }

    imgElement.src = imageUrls[0];

    if (imageUrls.length <= 1) {
      // No hover effect if there's only one image (or no images parsed)
      return;
    }

    let currentIndex = 1;
    let intervalId = null; // To store the interval timer

    card.addEventListener("mouseenter", () => {
      if (intervalId) clearInterval(intervalId); // Clear previous interval if any

      setTimeout(() => {
        imgElement.src = imageUrls[currentIndex]; // Show first image of cycle immediately
      }, 100); // Delay for 300ms before starting the cycle

      intervalId = setInterval(() => {
        currentIndex = (currentIndex + 1) % imageUrls.length;
        imgElement.src = imageUrls[currentIndex];
      }, 1200); // Change image every 1 second (1000 milliseconds)
    });

    card.addEventListener("mouseleave", () => {
      if (intervalId) clearInterval(intervalId); // Stop the image cycling
      intervalId = null;
      imgElement.src = imageUrls[0]; // Reset to first image
      currentIndex = 1; // Reset index
    });
  });

  const addToCartButtons = document.querySelectorAll(".add-to-cart-btn");
  addToCartButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      const productCode = button.dataset.productCode;
      const token = button.dataset.csrf;
      addToCart(productCode, token);
      window.location.reload(); // Reload page after adding to cart
    });
  });

  const addToCartButtonsSelected = document.querySelectorAll(
    ".add-to-cart-btn-selected"
  );
  addToCartButtonsSelected.forEach((button) => {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      const productCode = button.dataset.productCode;
      const token = button.dataset.csrf;
      removeFromCart(productCode, token);
    });
  });

  const filterBtn = document.getElementById("filterBtn");
  const filterPanel = document.getElementById("filterPanel");
  filterBtn &&
    filterBtn.addEventListener("click", () => {
      filterPanel.toggleAttribute("open");
    });

  if (window.location.search.includes("tags")) {
    filterPanel.toggleAttribute("open");
  }

  const sortBtn = document.getElementById("sortBtn");
  const sortMenu = document.getElementById("sortMenu");
  sortBtn &&
    sortBtn.addEventListener("click", () => {
      sortMenu.toggleAttribute("open");
    });

  const productGrid = document.getElementById("productGrid");
  document.getElementById("applyFilters")?.addEventListener("click", () => {
    const checkedSizes = Array.from(
      filterPanel.querySelectorAll('input[name="size"]:checked')
    ).map((cb) => cb.value);
    const checkedBrands = Array.from(
      filterPanel.querySelectorAll('input[name="brand"]:checked')
    ).map((cb) => cb.value);

    Array.from(productGrid.children).forEach((card) => {
      const size = card.dataset.size;
      const brand = card.dataset.brand;
      const sizeMatch = !checkedSizes.length || checkedSizes.includes(size);
      const brandMatch = !checkedBrands.length || checkedBrands.includes(brand);
      card.hidden = !(sizeMatch && brandMatch);
    });
  });

  sortMenu?.querySelectorAll("button")?.forEach((btn) => {
    btn.addEventListener("click", () => {
      sortMenu
        .querySelectorAll("button")
        .forEach((b) => b.removeAttribute("selected"));
      const sortType = btn.dataset.sort;
      const cards = Array.from(productGrid.children);
      console.log("Sorting by:", sortType);
      console.log("Number of cards:", cards.length);
      const compare = {
        price_asc: (a, b) => a.dataset.price - b.dataset.price,
        price_desc: (a, b) => b.dataset.price - a.dataset.price,
        year_asc: (a, b) => a.dataset.code - b.dataset.code,
        year_desc: (a, b) => b.dataset.code - a.dataset.code,
      }[sortType];
      productGrid.innerHTML = ""; // Clear existing cards
      cards.sort(compare).forEach((card) => productGrid.appendChild(card));
      btn.toggleAttribute("selected");
    });
  });
});
