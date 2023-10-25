pub mod mobaplayergen;

pub trait Generator<T> {
    fn generate() -> T;
}