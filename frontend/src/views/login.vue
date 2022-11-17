<template>
  <div class="container" v-loading="loading" element-loading-background="#8888">
    <viewHeader :panelTitle="'登录页面'"></viewHeader>
    <div class="formContainer">
      <div class="formHeader">
        妙思猜绘 <span style="font-size: 18px">{{mode == 'login'?'登录系统':'注册系统'}}</span>
      </div>
      <!-- 登录表单区域 -->
      <el-form :model="loginForm" status-icon :rules="rules" abel-position="right" ref="loginForm" label-width="80px" class="formBody">

        <el-form-item label="用户名:" prop="username">
          <el-input type="text" v-model="loginForm.username" autocomplete="off" maxlength="32" placeholder="同时支持邮箱登录"></el-input>
        </el-form-item>
        <el-form-item label="密码:" prop="password">
          <el-input type="password" v-model="loginForm.password" autocomplete="off" maxlength="32" placeholder="请输入密码..." @keyup.enter.native="submitLoginForm('loginForm')"></el-input>
        </el-form-item>
        <el-form-item v-show="mode == 'register'" label="电子邮箱:" prop="email">
          <el-input type="text" v-model="loginForm.email" autocomplete="off" maxlength="32" placeholder="请输入电子邮箱..."></el-input>
        </el-form-item>
        <el-form-item v-show="mode == 'register'" label="邮件验证:" prop="verify_code">
          <el-input class="verify_code_input" type="number" v-model="loginForm.verify_code" autocomplete="off" maxlength="6" placeholder="请输入邮件验证码...">
            <el-button :class="['get_verify_code_btn', smcBtnCls]" slot="append" type="primary" plain @click="submitVerifyForm('loginForm')" :disabled="this.sending_mail_code">{{sending_mail_code?"验证码已发送...":"获取邮件验证码"}}</el-button>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button v-show="mode == 'login'" type="primary" @click="submitLoginForm('loginForm')">登录</el-button>
          <el-button v-show="mode == 'register'" type="success" @click="submitRegisterForm('loginForm')">注册</el-button>
          <!-- <el-button @click="resetForm('loginForm')">重置</el-button> -->
          <span class="to_reg_text" @click="switch_loogin_register()">{{mode == 'login'?'还没有账号？去注册':'已有账号？去登录'}}</span>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import md5 from 'js-md5';
import viewHeader from '@/components/viewHeader.vue'

export default {
  components: {viewHeader},
  mounted() {
    setTimeout(() => {this.loading = false}, 500)
  },
  data() {
    let validateInput = (rule, value, callback) => {
      if (!this.checkSpecialKey(value)) {
        callback(new Error("输入不能含有特殊字符！"));
      } else {
        callback();
      }
    };
    let validatePassword = (rule, value, callback) => {
      if (!this.checkSpecialKey(value)) {
        callback(new Error("输入不能含有特殊字符！"));
      } else {
        callback();
      }
    };
    let validateEmail = (rule, value, callback) => {
      if (!this.checkSpecialKey(value)) {
        callback(new Error("输入不能含有特殊字符！"));
      } else {
        callback();
      }
    };
    return {
      mode: 'login',
      loading: true,
      sending_mail_code: false,
      smcBtnCls: '',
      loginForm: {
        username: '',
        password: '',
        email: '',
        verify_code: '',
      },
      rules: {
        username: [
          { validator: validateInput, trigger: 'blur' }
        ],
        password: [
          { validator: validatePassword, trigger: 'blur' }
        ],
        email: [
          { validator: validateEmail, trigger: 'blur' }
        ],
        verify_code: [
          { validator: validateEmail, trigger: 'blur' }
        ],
      },
    };
  },
  methods: {
    // 校验输入框不能有特殊字符
    checkSpecialKey(str) {
      let specialKey = "[`^*()=|{}':;'\\[\\]<>/！￥……&*（）——|{}【】‘；：”“'。，、？]‘'";
      for (let i = 0; i < str.length; i++) {
        if (specialKey.indexOf(str.substr(i, 1)) != -1) {
          return false;
        }
      }
      return true;
    },
    // 提交登录请求
    submitLoginForm(formName) {
      let _this = this
      this.$refs[formName].validate((valid) => {
        if (valid) {
          _this.$http({
            method: 'post',
            url: '/api/login',
            data: {
              username: _this.loginForm.username,
              credential: md5(_this.loginForm.password),
            }
          })
            .then((res) => {
              if(res.data.code == 'success') {
                _this.$message({type: 'success', message: res.data.msg, duration: 2000})
                _this.$store.commit('setUsername', res.data.username)
                sessionStorage.setItem("username", res.data.username)
                _this.$router.push('/')
              } else {
                _this.$message({type: 'error', message: res.data.msg, duration: 2000})
              }
            })
            .catch(function (error) {
              _this.$message({type: 'error', message: '登录失败，请检查用户名和密码是否有误', duration: 2000})
            });

        } else {
          _this.$message({type: 'error', message: '校验失败，请检查输入内容', duration: 2000})
        }
      });
    },
    // 提交注册请求
    submitRegisterForm(formName) {
      let _this = this
      this.$refs[formName].validate((valid) => {
        if (valid) {
          _this.$http({
            method: 'post',
            url: '/api/register',
            data: {
              username: _this.loginForm.username,
              credential: md5(_this.loginForm.password),
              email: _this.loginForm.email,
              verify_code: _this.loginForm.verify_code,
            }
          })
            .then((res) => {
              if(res.data.code == 'success') {
                _this.$message({type: 'success', message: res.data.msg, duration: 2000})
                setTimeout(() => {
                  _this.switch_loogin_register()
                }, 200);
              } else {
                _this.$message({type: 'error', message: res.data.msg, duration: 2000})
              }
            })
            .catch(function (error) {
              _this.$message({type: 'error', message: '注册失败，请检查用户信息是否有误', duration: 2000})
            });
            
        } else {
          _this.$message({type: 'error', message: '校验失败，请检查输入内容', duration: 2000})
        }
      });
    },
    // 提交邮件验证请求
    submitVerifyForm(formName) {
      let _this = this
      this.$refs[formName].validate((valid) => {
        if (valid) {
          _this.sending_mail_code = true
          _this.smcBtnCls='get_verify_code_btn_activated'

          _this.$http({
            method: 'post',
            url: '/api/req_email_vertify',
            data: {
              email: _this.loginForm.email,
            }
          })
            .then((res) => {
              if(res.data.code == 'success') {
                _this.$message({type: 'success', message: res.data.msg, duration: 2000})
                setTimeout(() => {_this.sending_mail_code = false; _this.smcBtnCls=''}, 20000)
              } else {
                _this.$message({type: 'error', message: res.data.msg, duration: 2000})
              }
            })
            .catch(function (error) {
              _this.$message({type: 'error', message: '发送失败，请检查邮箱地址是否有误', duration: 2000})
            });

        } else {
          _this.$message({type: 'error', message: '校验失败，请检查输入内容', duration: 2000})
        }
      });
    },
    // 重置表单
    resetForm(formName) {
      this.$refs[formName].resetFields();
    },
    // 切换登录与注册
    switch_loogin_register() {
      this.loading = true;
      setTimeout(() => {
        if(this.mode == 'login') {
          this.mode = 'register'
        } else {
          this.mode = 'login'
        }
        this.resetForm('loginForm')
        setTimeout(() => {this.loading = false}, 250)
      }, 250)
    },
  }
}
</script>
<style lang="scss">
* {
  transition: all 0.5s;
}
.container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  .formContainer {

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    padding: 0 40px;
    border-radius: 18px;
    background: #ffffff88;
    box-shadow:  -14px -14px 28px #55555552, 14px 14px 28px #57575762;
    overflow: hidden;

    .formHeader {
      width: 100%;
      height: 80px;
      padding: 0 40px;
      background-color: #92459c88;

      color: white;
      text-shadow: 2px 2px 8px #0008;
      font-size: 28px;
      line-height: 80px;
    }

    .formBody {
      width: 100%;
      padding: 40px 20px 0;

      .to_reg_text {
        color: #409EFF;
        margin-left: 10px;
      }

      .el-button {
        margin: 0;
      }
      
      .get_verify_code_btn {
        color: #FFF;
        background-color: #409EFF;
        border-color: #409EFF;
        transition: all 0.5s;
      }

      .get_verify_code_btn_activated {
        color: #fff;
        background-color: #909399;
        border-color: #909399;
      }

      .el-input-group__append {
        padding: 0;
      }
    }
  }
}
</style>