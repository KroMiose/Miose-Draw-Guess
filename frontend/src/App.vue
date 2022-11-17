<template>
  <div id="app">
    <router-view/>
  </div>
</template>
<script>
export default {
  mounted() {
    document.body.addEventListener('touchmove', function (e) {
      e.preventDefault(); //阻止默认的处理方式(阻止下拉滑动的效果)
    }, {passive: false}); //passive 参数不能省略，用来兼容ios和android
    // window.addEventListener(
    //   "touchmove",
    //   function(event) {
    //   if (event.scale !== 1) {
    //   event.preventDefault();
    //   }
    //   },
    //   { passive: false }
    // );
    try {
      // 禁用双击缩放
      // document.addEventListener("touchstart", function(event) {
      //   if (event.touches.length > 1) {
      //     event.preventDefault();
      //   }
      // });
      var lastTouchEnd = 0;
      document.addEventListener(
        "touchend",
        function(event) {
          var now = new Date().getTime();
          if (now - lastTouchEnd <= 300) {
            event.preventDefault();
          }
          lastTouchEnd = now;
        },
        false
      );
      // 禁用双指手势操作
      document.addEventListener("gesturestart", function(event) {
        event.preventDefault();
      });
    } catch (error) {}
  }
}
</script>
<style lang="scss">
#app {
  width: 100%;
  height: 100%;
  user-select: none;

  background: #A770EF;  /* fallback for old browsers */
  background: -webkit-linear-gradient(to left, #FDB99B, #CF8BF3, #A770EF);  /* Chrome 10-25, Safari 5.1-6 */
  background: linear-gradient(to left, #FDB99B, #CF8BF3, #A770EF); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */

  .el-input__inner {
    background-color: #fffb;
    border-radius: 18px;
    box-shadow: #0003 4px 4px 16px;

  }
  .el-input__count .el-input__count-inner {
    background-color: #fff0;
  }

  .el-button {
    border-radius: 18px;
    margin: 0 10px;
    box-shadow: #0003 4px 4px 16px;
  }

  .el-input-group__append {
    background-color: #0000;
    border: none;
  }

  input[type=number]::-webkit-inner-spin-button, input[type=number]::-webkit-outer-spin-button { 
    appearance: none;
    -webkit-appearance: none;
    margin: 0;
  }
  input[type=number] {
    appearance: textfield;
    -moz-appearance: textfield;
  }
}

html body .el-message {
  background-color: #fff9;
  border-color: #fff6;
  min-width: 360px;
  border-radius: 18px;

  .el-message__icon {
    font-size: 18px;
  }

  .el-message__content {
    font-size: 18px;
  }
}
</style>
