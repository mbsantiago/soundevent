$("pre.json").each(function (i, obj) {
  var json_str = $(obj).html();
  var json_obj = JSON.parse(json_str);
  $(obj).jsonViewer(json_obj, {
    collapsed: true,
    rootCollapsable: false,
    withQuotes: true,
  });
});
