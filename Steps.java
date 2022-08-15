import io.cucumber.java.pt.*;
import io.restassured.response.Response;
import org.hamcrest.Matchers;
import static io.restassured.RestAssured.given;

public class PessoasSteps {
    private Response response;

    private static final String URL = "http://localhost:8080/pessoas"; 

    @Quando(" eu gravar uma nova pessoa de {string} {string} e {string} {string}  ") 
    public void euPesquisarAPessoaDeDocumento(  String documento, String documentoValor, String nome, String nomeValor ) {
        response = given().when().body("{  " + documento + ": " + documentoValor + ", " + nome + ": " + nomeValor + "}").post(URL);
    }
}