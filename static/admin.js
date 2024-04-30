$(document).ready(function () {
    // Fetch the price list on startup
    fetch("/get_price_list")
        .then((response) => response.json())
        .then((data) => {
            // Iterate over each category
            data.categories.forEach((category) => {
                var categoryHTML =
                    '<div class="category">' +
                    '<input type="text" name="categoryName" placeholder="Category Name" value="' +
                    category.name +
                    '">' +
                    '<div class="entries">';

                // Iterate over each entry in this category
                category.entries.forEach((entry) => {
                    categoryHTML +=
                        '<div class="entry">' +
                        '<input type="text" name="entryName" placeholder="Product Name" value="' +
                        entry.name +
                        '">' +
                        '<input type="text" name="entrySold" placeholder="Product Amount" value="' +
                        entry.amount +
                        '">' +
                        '<input type="text" name="entryPrice" placeholder="Product Price" value="' +
                        entry.price +
                        '">' +
                        '<button type="button" class="removeEntry">Remove Product</button>' +
                        "</div>";
                });

                categoryHTML +=
                    "</div>" +
                    "<div class='buttons'>" +
                    '<button type="button" class="addEntry">Add Product</button>' +
                    '<button type="button" class="removeCategory">Remove Category</button>' +
                    "</div>" +
                    "</div>";

                $("#categories").append(categoryHTML);
            });
        })
        .catch((error) => {
            console.error("Error:", error);
        });

    fetch("/get_show_spotify")
        .then((response) => response.json())
        .then((data) => {
            $("#enable-spotify").prop("checked", data.enable);
        })
        .catch((error) => {
            console.error("Error:", error);
        });

    $("#addCategory").click(function () {
        var categoryHTML =
            '<div class="category">' +
            '<input type="text" name="categoryName" placeholder="Category Name">' +
            '<div class="entries">' +
            '<div class="entry">' +
            '<input type="text" name="entryName" placeholder="Product Name">' +
            '<input type="text" name="entrySold" placeholder="Product amount">' +
            '<input type="text" name="entryPrice" placeholder="Product Price">' +
            '<button type="button" class="removeEntry">Remove Product</button>' +
            "</div>" +
            "</div>" +
            "<div class='buttons'>" +
            '<button type="button" class="addEntry">Add Product</button>' +
            '<button type="button" class="removeCategory">Remove Category</button>' +
            "</div>" +
            "</div>";

        $("#categories").append(categoryHTML);
    });

    $(document).on("click", ".addEntry", function () {
        var entryHTML =
            '<div class="entry">' +
            '<input type="text" name="entryName" placeholder="Product Name">' +
            '<input type="text" name="entrySold" placeholder="Product Amount">' +
            '<input type="text" name="entryPrice" placeholder="Product Price">' +
            '<button type="button" class="removeEntry">Remove Product</button>' +
            "</div>";

        $(this).parent().siblings(".entries").append(entryHTML);
    });

    $(document).on("click", ".removeCategory", function () {
        $(this).parent().parent(".category").remove();
    });

    $(document).on("click", ".removeEntry", function () {
        $(this).parent(".entry").remove();
    });

    $("#enable-spotify").change(function () {
        var showSpotify = this.checked; // true if checked, false otherwise

        // Create the JSON string
        var json = {
            enable: showSpotify,
        };

        // Send the JSON string to the server endpoint
        fetch("/administrate/set_show_spotify", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(json),
        })
            .then((response) => response.json())
            .then((data) => console.log(data))
            .catch((error) => {
                console.error("Error:", error);
            });
    });

    $("#submit-button").click(function (e) {
        e.preventDefault();

        // Create the JSON string
        var json = {
            categories: [],
        };

        // Iterate over each category
        $(".category").each(function () {
            var category = {
                name: $(this).find('input[name="categoryName"]').val(),
                entries: [],
            };

            // Iterate over each entry in this category
            $(this)
                .find(".entry")
                .each(function () {
                    var entry = {
                        name: $(this).find('input[name="entryName"]').val(),
                        price: $(this).find('input[name="entryPrice"]').val(),
                        amount: $(this).find('input[name="entrySold"]').val(),
                    };

                    category.entries.push(entry);
                });

            json.categories.push(category);
        });

        console.log(json);

        // Send the JSON string to the server endpoint
        fetch("/administrate/set_price_list", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(json),
        })
            .then((response) => response.json())
            .then((data) => console.log(data))
            .catch((error) => {
                console.error("Error:", error);
            });
    });
});
