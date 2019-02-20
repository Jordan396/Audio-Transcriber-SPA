<template>
  <div>
    <section class="hero is-primary">
      <div class="hero-body">
        <div class="container has-text-centered">
          <h2 class="title">404 Not Found</h2>
        </div>
      </div>
    </section>
    <div class="container is-fluid" id="main-container">
      <div class="notification">
        <div class="row has-text-centered">
          <img src="./../assets/404NotFound.jpg" alt="404NotFound">
        </div>
        <div class="row has-text-centered">
          <h1>Oops!</h1>
        </div>
        <div class="row has-text-centered">
          <h4>We can't seem to find the page you're looking for.</h4>
        </div>
        <div class="row has-text-centered"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
#main-container {
  padding-top: 40px;
}
.row.has-text-centered {
  padding-top: 20px;
}
h1 {
  font-size: 40px;
}
</style>