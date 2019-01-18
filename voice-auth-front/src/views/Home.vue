<template>
  <div>
    <header>Voice Auth</header>
    <div class="content">
      <div class="content-item">
        <div>
          <input type="text" v-model="newUser" placeholder="New username">
        </div>
        <div class="button">Record voice</div>
        <div class="output">{{recordResult}}</div>
      </div>
      <div class="content-item">
        <div class="button">Sign In</div>
        <div class="output">{{signResult}}</div>
      </div>
      <div class="content-item">
        <div class="button">Clear Database</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      newUser: "",
      recordResult: "Ready",
      signResult: "Ready"
    };
  },
  methods: {

  }
};
</script>

<style>
header {
  margin: 80px;
  font-size: 28px;
}
input {
  width: 200px;
}
.content {
  display: flex;
  justify-content: center;
}
.content-item {
  align-self: center;
  margin: 20px;
}
.output {
  margin-top: 10px;
  word-wrap: normal;
}
.button {
  font-size: 16px;
  text-align: center;
  background-color: black;
  margin: auto;
  margin-top: 10px;
  cursor: pointer;
  color: white;
  width: 200px;
  padding: 10px;
  max-height: 20px;
}
</style>
