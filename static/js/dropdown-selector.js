window.addEventListener('load', function () {
    $(".list__ul a").on("click", function (ev) {
        $("#ghost-name-submit-btn").show()
    });

    $(".placeholder").on("click", function (ev) {
        $(".placeholder").css("opacity", "0");
        $(".list__ul").toggle();
        $('.ghost-description-span').hide();
    });

    $(".list__ul a").on("click", function (ev) {
        ev.preventDefault();
        var index = $(this)
            .parent()
            .index();

        $(".placeholder")
            .text($(this).text())
            .css("opacity", "1");

        $("input[name='selected-ghost-id']").val($(this).attr("value"));
        $("input[name='selected-ghost-name']").val($(this).text());

        console.log(
            $(".list__ul")
                .find("li")
                .eq(index)
                .html()
        );

        $('.ghost-description-span[value=' + $(this).attr("value") + ']').toggle()

        $(".list__ul")
            .find("li")
            .eq(index)
            // .text('/"' + $(this).text() + '/"')
            .prependTo(".list__ul");
        $(".list__ul").toggle();
    });

    $("select").on("change", function (e) {
        // Set text on placeholder hidden element
        $(".placeholder").text(' /"' + this.value + ' /"');

        // Animate select width as placeholder
        $(this).animate({ width: $(".placeholder").width() + "px" });
    });
});