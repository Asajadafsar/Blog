// import { AuthProvider, HttpError } from "react-admin";
// import axios from 'axios';

// export const authProvider: AuthProvider = {
//   login: ({ username, password }) => {
//     const data = JSON.stringify({
//       "username": username,
//       "password": password
//     });

//     const config = {
//       method: 'POST',
//       url: 'http://127.0.0.1:8000/sign/login/',
//       headers: { 
//         'Content-Type': 'application/json'
//       },
//       data: data
//     };

//     return axios.request(config)
//       .then((response) => {
//         if (response.status === 200) {
//           const token = response.data.token;
//           localStorage.setItem("token", token);
//           return axios.get('http://127.0.0.1:8000/sign/profile/', {
//             headers: { 'Authorization': `Bearer ${token}` }
//           });
//         } else {
//           throw new Error("Login failed");
//         }
//       })
//       .then((profileResponse) => {
//         if (profileResponse.data.role !== 'admin') {
//           throw new Error("Unauthorized access");
//         }
//       })
//       .catch((error) => {
//         console.error(error.message || "An error occurred");
//         throw new HttpError("Unauthorized access", 401);
//       });
//   },
//   logout: () => {
//     localStorage.removeItem("token");
//     return Promise.resolve();
//   },
//   checkError: ({ status }) => {
//     if (status === 401 || status === 403) {
//       localStorage.removeItem("token");
//       return Promise.reject();
//     }
//     return Promise.resolve();
//   },
//   checkAuth: () => {
//     return localStorage.getItem("token") ? Promise.resolve() : Promise.reject();
//   },
//   getPermissions: () => Promise.resolve(),
//   getIdentity: () => {
//     const token = localStorage.getItem("token");
//     if (!token) {
//       return Promise.reject(new Error("No token found"));
//     }

//     const config = {
//       method: 'get',
//       url: 'http://127.0.0.1:8000/sign/profile/',
//       headers: { 
//         'Authorization': `Bearer ${token}`
//       }
//     };

//     return axios.request(config)
//       .then((response) => {
//         if (response.data.role === 'admin') {
//           return Promise.resolve(response.data);
//         } else {
//           throw new Error("Unauthorized access");
//         }
//       })
//       .catch((error) => {
//         throw new Error("Unauthorized access");
//       });
//   },
// };

// export default authProvider;
import { AuthProvider, HttpError } from "react-admin";
import axios from 'axios';

export const authProvider: AuthProvider = {
  login: ({ username, password }) => {
    const data = JSON.stringify({
      "username": username,
      "password": password
    });

    const config = {
      method: 'POST',
      url: 'http://127.0.0.1:8000/sign/login/',
      headers: { 
        'Content-Type': 'application/json'
      },
      data: data
    };

    return axios.request(config)
      .then((response) => {
        if (response.status === 200) {
          const token = response.data.token;
          localStorage.setItem("token", token);
        } else {
          throw new Error("Login failed");
        }
      })
      .catch((error) => {
        console.error(error.message || "An error occurred");
        throw new HttpError("Unauthorized access", 401);
      });
  },
  logout: () => {
    localStorage.removeItem("token");
    return Promise.resolve();
  },
  checkError: ({ status }) => {
    if (status === 401 || status === 403) {
      localStorage.removeItem("token");
      return Promise.reject();
    }
    return Promise.resolve();
  },
  checkAuth: () => {
    return localStorage.getItem("token") ? Promise.resolve() : Promise.reject();
  },
  getPermissions: () => Promise.resolve(),
  _getIdentity: () => {
    const token = localStorage.getItem("token");
    if (!token) {
      return Promise.reject(new Error("No token found"));
    }

    // If we only need to check for the existence of the token
    return Promise.resolve({ token });
  },
  get getIdentity() {
    return this._getIdentity;
  },
  set getIdentity(value) {
    this._getIdentity = value;
  },
};

export default authProvider;
