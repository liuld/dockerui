$(function () {
    // 点击展开下拉菜单
    let app_menu = $(".app-menu");
    app_menu.on("click", ".app-menu__item[data-toggle=treeview]", function (event) {
        let treeview = $(event.target).closest(".treeview");
        treeview.siblings("li").removeClass("is-expanded");
        treeview.toggleClass("is-expanded");
    });
    // 二级菜单点击添加样式
    let dashboard_item = $(".app-menu__item[data-toggle!=treeview]");
    let treeview_item = $(".treeview-menu .treeview-item");
    dashboard_item.on("click", function () {
        treeview_item.removeClass("active");
        $(".app-menu .treeview").removeClass("is-expanded");
        dashboard_item.addClass("active");
        sessionStorage.setItem("active_item", JSON.stringify([0, 0]));
    });
    $(".treeview-menu").on("click", ".treeview-item", function (event) {
        let active_item_element = $(event.target).closest("li");
        let active_item_parent_element = active_item_element.parents("li.treeview");
        let active_index = [active_item_parent_element.index(), active_item_element.index()];
        treeview_item.removeClass("active");
        dashboard_item.removeClass("active");
        $(event.target).addClass("active");
        sessionStorage.setItem("active_item", JSON.stringify(active_index));
    });
    //从sessionStorage中获取active item并设置样式
    let active_item = $.parseJSON(sessionStorage.getItem("active_item"));
    if (active_item) {
        if (active_item[0] === 0){
            dashboard_item.addClass("active");
        }else{
            let active_parent_item = app_menu.children("li").eq(active_item[0]);
            let active_children_item = active_parent_item.children("ul").eq(0).children("li").eq(active_item[1]);
            dashboard_item.removeClass("active");
            treeview_item.removeClass("active");
            active_children_item.children("a.treeview-item").addClass("active");
            active_parent_item.addClass("is-expanded");
        }
    }
    //小图标显示菜单
    $("a[data-toggle=sideMenu]").on("click", function () {
        $("body.app").toggleClass("mini");
    });
});
