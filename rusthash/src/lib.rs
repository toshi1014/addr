use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use tiny_keccak::{Hasher, Keccak};

#[no_mangle]
pub extern "C" fn keccak(src: *const c_char) -> *const c_char {
    let c_str: &CStr = unsafe { CStr::from_ptr(src) };
    let data: &str = c_str.to_str().unwrap();

    let mut sha3 = Keccak::v256();
    let mut hashed = [0u8; 32];
    let byte = hex::decode(data).expect("hex conversion failed");
    sha3.update(&byte);
    sha3.finalize(&mut hashed);

    let hex_str = hashed.map(|dec: u8| format!("{:0>2x}", dec)).join("");
    let c_str: CString = CString::new(hex_str).unwrap();
    let c_str_ptr: *const c_char = c_str.as_ptr();
    std::mem::forget(c_str);

    c_str_ptr
}
