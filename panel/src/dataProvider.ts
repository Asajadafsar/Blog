import axios from 'axios';
import { stringify } from 'query-string';
import { DataProvider } from 'react-admin';

const apiUrl = 'http://localhost:8000';

const httpClient = axios.create({
  baseURL: apiUrl,
});

httpClient.interceptors.request.use(
  (config) => {
    // Retrieve the token from local storage
    const token = localStorage.getItem('token');

    // Check if a token exists
    if (token) {
      // Add the Authorization header with the token
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // Add any other headers if needed
    config.headers['Barber'] = 'SomeValue';

    return config;
  },
  (error) => {
    // Handle request errors
    return Promise.reject(error);
  }
);

const dataProvider: DataProvider = {
  getList: (resource, params) => {
    const { page, perPage } = params.pagination;
    const { field, order } = params.sort;
    const query = {
      sort: JSON.stringify([field, order]),
      range: JSON.stringify([(page - 1) * perPage, page * perPage - 1]),
      filter: JSON.stringify(params.filter),
    };
    const url = `/${resource}?${stringify(query)}`;

    return httpClient.get(url).then(response => ({
      data: response.data,
      total: parseInt(response.headers['x-total-count'], 10),
    }));
  },
  getOne: (resource, params) =>
    httpClient.get(`/${resource}/${params.id}`).then(response => ({
      data: response.data,
    })),
  getMany: (resource, params) => {
    const query = {
      filter: JSON.stringify({ id: params.ids }),
    };
    const url = `/${resource}?${stringify(query)}`;
    return httpClient.get(url).then(response => ({
      data: response.data,
    }));
  },
  getManyReference: (resource, params) => {
    const { page, perPage } = params.pagination;
    const { field, order } = params.sort;
    const query = {
      sort: JSON.stringify([field, order]),
      range: JSON.stringify([(page - 1) * perPage, page * perPage - 1]),
      filter: JSON.stringify({ ...params.filter, [params.target]: params.id }),
    };
    const url = `/${resource}?${stringify(query)}`;
    return httpClient.get(url).then(response => ({
      data: response.data,
      total: parseInt(response.headers['x-total-count']),
    }));
  },
  update: (resource, params) => {
    if (resource === 'users' && params.data.profile_picture) {
      const formData = new FormData();
      Object.keys(params.data).forEach(key => {
        if (key === 'profile_picture' && params.data[key].rawFile) {
          formData.append(key, params.data[key].rawFile);
        } else {
          formData.append(key, params.data[key]);
        }
      });
      return httpClient.put(`/${resource}/${params.id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }).then(response => ({ data: response.data }));
    } else if (resource === 'blog_posts' && params.data.image) { // اضافه کردن برای ادیت عکس پست
      const formData = new FormData();
      Object.keys(params.data).forEach(key => {
        if (key === 'image' && params.data[key].rawFile) {
          formData.append(key, params.data[key].rawFile);
        } else {
          formData.append(key, params.data[key]);
        }
      });
      return httpClient.put(`/${resource}/${params.id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }).then(response => ({ data: response.data }));
    } else {
      return httpClient.put(`/${resource}/${params.id}`, params.data).then(response => ({ data: response.data }));
    }
  },
  

create: (resource, params) => {
  if (resource === 'users' && params.data.profile_picture) {
      const formData = new FormData();
      Object.keys(params.data).forEach(key => {
          if (key === 'profile_picture' && params.data[key].rawFile) {
              formData.append(key, params.data[key].rawFile);
          } else {
              formData.append(key, params.data[key]);
          }
      });
      return httpClient.post(`/${resource}`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
      }).then(response => ({ data: response.data }));
  } else {
      return httpClient.post(`/${resource}`, params.data).then(response => ({ data: response.data }));
  }
},
  delete: (resource, params) =>
    httpClient.delete(`/${resource}/${params.id}`).then(response => ({
      data: response.data,
    })),
  deleteMany: (resource, params) => {
    const ids = params.ids;
    const deletePromises = ids.map(id =>
      httpClient.delete(`/${resource}/${id}`)
    );
    return Promise.all(deletePromises).then(responses => ({
      data: responses.map(response => response.data)
    }));
  },
};

export default dataProvider;
