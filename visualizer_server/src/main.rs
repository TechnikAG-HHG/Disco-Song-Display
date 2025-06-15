use rweb::*;

const PORT: u16 = 5000;

#[get("/")]
fn index() -> impl Reply {
    // return html file
    let html = include_str!("../../visualizer/dist/index.html");
    rweb::reply::html(html)
}

#[get("/static/{path}")]
fn static_file(path: String) -> impl Reply {
    // return static file
    let file_path = format!("../../visualizer/dist/{}", path);
    println!("Serving static file: {}", file_path);
    let file = std::fs::read(&file_path).unwrap();
    let mime = mime_guess::from_path(&file_path).first_or_octet_stream();
    rweb::reply::with_header(rweb::reply::html(file), "Content-Type", mime.to_string())
}

#[tokio::main]
async fn main() {
    println!("Hello, world!");
    serve(index()).run(([0, 0, 0, 0], PORT)).await;
}
