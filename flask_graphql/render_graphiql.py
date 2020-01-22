from flask import render_template_string
import os
this_py_file = os.path.realpath(__file__)
this_dir = os.path.split(this_py_file)[0]
GRAPHIQL_VERSION = '0.11.11'

with open(os.path.join(this_dir, 'fetch.min.js'), 'r') as js:
    fetch_min_js =  js.read()

with open(os.path.join(this_dir, 'react.min.js'), 'r') as js:
    react_min_js = js.read()

with open(os.path.join(this_dir, 'react-dom.min.js'), 'r') as js:
    react_dom_min_js = js.read()

with open(os.path.join(this_dir, 'graphiql.min.js'), 'r') as js:
    graphiql_min_js = js.read()

with open(os.path.join(this_dir, 'graphiql.css'), 'r') as css:
    graphiql_css = css.read()


T1 = '''<!--
The request to this GraphQL server provided the header "Accept: text/html"
and as a result has been presented GraphiQL - an in-browser IDE for
exploring GraphQL.
If you wish to receive JSON, provide the header "Accept: application/json" or
add "&raw" to the end of the URL within a browser.
-->
<!DOCTYPE html>
<html>
<head>
  <title>{{graphiql_html_title|default("GraphiQL", true)}}</title>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      overflow: hidden;
      width: 100%;
    }
'''
T2 = f'''
  </style>
  <meta name="referrer" content="no-referrer">
  <style>  { graphiql_css } </style>
  <script> { fetch_min_js } </script>
  <script> { react_min_js } </script>
  <script> { react_dom_min_js } </script>
  <script> { graphiql_min_js } </script>
'''

T3 = '''
</head>
<body>
  <script>
    // Collect the URL parameters
    var parameters = {};
    window.location.search.substr(1).split('&').forEach(function (entry) {
      var eq = entry.indexOf('=');
      if (eq >= 0) {
        parameters[decodeURIComponent(entry.slice(0, eq))] =
          decodeURIComponent(entry.slice(eq + 1));
      }
    });

    // Produce a Location query string from a parameter object.
    function locationQuery(params) {
      return '?' + Object.keys(params).map(function (key) {
        return encodeURIComponent(key) + '=' +
          encodeURIComponent(params[key]);
      }).join('&');
    }

    // Derive a fetch URL from the current URL, sans the GraphQL parameters.
    var graphqlParamNames = {
      query: true,
      variables: true,
      operationName: true
    };

    var otherParams = {};
    for (var k in parameters) {
      if (parameters.hasOwnProperty(k) && graphqlParamNames[k] !== true) {
        otherParams[k] = parameters[k];
      }
    }
    var fetchURL = locationQuery(otherParams);

    // Defines a GraphQL fetcher using the fetch API.
    function graphQLFetcher(graphQLParams) {
      return fetch(fetchURL, {
        method: 'post',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(graphQLParams),
        credentials: 'include',
      }).then(function (response) {
        return response.text();
      }).then(function (responseBody) {
        try {
          return JSON.parse(responseBody);
        } catch (error) {
          return responseBody;
        }
      });
    }

    // When the query and variables string is edited, update the URL bar so
    // that it can be easily shared.
    function onEditQuery(newQuery) {
      parameters.query = newQuery;
      updateURL();
    }

    function onEditVariables(newVariables) {
      parameters.variables = newVariables;
      updateURL();
    }

    function onEditOperationName(newOperationName) {
      parameters.operationName = newOperationName;
      updateURL();
    }

    function updateURL() {
      history.replaceState(null, null, locationQuery(parameters));
    }

    // Render <GraphiQL /> into the body.
    ReactDOM.render(
      React.createElement(GraphiQL, {
        fetcher: graphQLFetcher,
        onEditQuery: onEditQuery,
        onEditVariables: onEditVariables,
        onEditOperationName: onEditOperationName,
        query: {{ params.query|tojson }},
        response: {{ result|tojson }},
        variables: {{ params.variables|tojson }},
        operationName: {{ params.operation_name|tojson }},
      }),
      document.body
    );
  </script>
</body>
</html>'''

TEMPLATE = T1 + T2 + T3

def render_graphiql(params, result, graphiql_version=None,
                    graphiql_template=None, graphiql_html_title=None):
    graphiql_version = graphiql_version or GRAPHIQL_VERSION
    template = graphiql_template or TEMPLATE

    return render_template_string(
        template,
        graphiql_version=graphiql_version,
        graphiql_html_title=graphiql_html_title,
        result=result,
        params=params
    )

if __name__ == '__main__':
    print(fetch_min_js)
    print(graphiql_css)
    print(graphiql_min_js)
    print(react_dom_min_js)
    print(react_min_js)

