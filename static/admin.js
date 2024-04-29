$(document).ready(function () {
    $("#addCategory").click(function () {
        var categoryHTML =
            '<div class="category">' +
            '<input type="text" name="categoryName" placeholder="Category Name">' +
            '<div class="entries">' +
            '<div class="entry">' +
            '<input type="text" name="entryName" placeholder="Entry Name">' +
            '<input type="text" name="entryPrice" placeholder="Entry Price">' +
            '<button type="button" class="removeEntry">Remove Entry</button>' +
            "</div>" +
            "</div>" +
            '<button type="button" class="addEntry">Add Entry</button>' +
            '<button type="button" class="removeCategory">Remove Category</button>' +
            "</div>";

        $("#categories").append(categoryHTML);
    });

    $(document).on("click", ".addEntry", function () {
        var entryHTML =
            '<div class="entry">' +
            '<input type="text" name="entryName" placeholder="Entry Name">' +
            '<input type="text" name="entryPrice" placeholder="Entry Price">' +
            '<button type="button" class="removeEntry">Remove Entry</button>' +
            "</div>";

        $(this).siblings(".entries").append(entryHTML);
    });

    $(document).on("click", ".removeCategory", function () {
        $(this).parent(".category").remove();
    });

    $(document).on("click", ".removeEntry", function () {
        $(this).parent(".entry").remove();
    });

    $("#pricelistForm").submit(function (e) {
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
                    };

                    category.entries.push(entry);
                });

            json.categories.push(category);
        });

        console.log(json);

        // Send the JSON string to the server endpoint
        fetch("/server-endpoint", {
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
