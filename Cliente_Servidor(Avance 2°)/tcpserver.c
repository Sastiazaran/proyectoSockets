/*

   Lectura remota de una palabra para devolver el numero de vocales usando sockets pertenecientes
   a la familia TCP, en modo conexion.
   Codigo del servidor

   Nombre Archivo: tcpserver.c
   Archivos relacionados: num_vocales.h tcpclient.c 
   Fecha: Febrero 2023

   Compilacion: cc tcpserver.c -lnsl -o tcpserver
   Ejecución: ./tcpserver
*/

#include <stdio.h>
/* The following headers was required in old or some compilers*/
//#include <sys/types.h>
//#include <sys/socket.h>
//#include <netinet/in.h>
#include <netdb.h>
#include <signal.h>	// it is required to call signal handler functions
#include <unistd.h>  // it is required to close the socket descriptor
#include "num_vocales.h"
#include "code.h"

#define  DIRSIZE   2048      /* longitud maxima parametro entrada/salida */
#define  PUERTO   15000	     /* numero puerto arbitrario */

int                  sd, sd_actual;  /* descriptores de sockets */
int                  addrlen;        /* longitud direcciones */
struct sockaddr_in   sind, pin;      /* direcciones sockets cliente u servidor */


/*  procedimiento de aborte del servidor, si llega una senal SIGINT */
/* ( <ctrl> <c> ) se cierra el socket y se aborta el programa       */
void aborta_handler(int sig){
   printf("....abortando el proceso servidor %d\n",sig);
   close(sd);  
   close(sd_actual); 
   exit(1);
}


int main(){
  
	char  dir[DIRSIZE];	     /* parametro entrada y salida */

	/*
	When the user presses <Ctrl + C>, the aborta_handler function will be called, 
	and such a message will be printed. 
	Note that the signal function returns SIG_ERR if it is unable to set the 
	signal handler, executing line 54.
	*/	
   if(signal(SIGINT, aborta_handler) == SIG_ERR){
   	perror("Could not set signal handler");
      return 1;
   }
       //signal(SIGINT, aborta);      /* activando la senal SIGINT */

/* obtencion de un socket tipo internet */
	if ((sd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
		perror("socket");
		exit(1);
	}

/* asignar direcciones en la estructura de direcciones */
	sind.sin_family = AF_INET;
	sind.sin_addr.s_addr = INADDR_ANY;   /* INADDR_ANY=0x000000 = yo mismo */
	sind.sin_port = htons(PUERTO);       /*  convirtiendo a formato red */

/* asociando el socket al numero de puerto */
	if (bind(sd, (struct sockaddr *)&sind, sizeof(sind)) == -1) {
		perror("bind");
		exit(1);
	}

/* ponerse a escuchar a traves del socket */
	if (listen(sd, 5) == -1) {
		perror("listen");
		exit(1);
	}

int max = 4;
pid_t child_pid;
for(int i = 0; i < max; i++){
		/* esperando que un cliente solicite un servicio */
		if ((sd_actual = accept(sd, (struct sockaddr *)&pin, &addrlen)) == -1) {
			perror("accept");
			exit(1);
		}
		child_pid = fork();
		if(child_pid == 0){
			break;
		}else{
			close(sd_actual);
		}
	}

	
	if(child_pid == 0){
			//child
			/* tomar un mensaje del cliente */
			if (recv(sd_actual, dir, sizeof(dir), 0) == -1) {
				perror("recv");
				exit(1);
			}

			/* leyendo el directorio */
				//num_vocales(dir);
				
				char msg[1000] = "";
				mathExpress(dir);
				//convert msg received to json format
				strcpy(msg,"{'");
				strcat(msg, "result");
				strcat(msg,"' : '");
				strcat(msg, dir);
				strcat(msg, "'},");
				//----------------------------------
				printf("%s \n", msg);
			/* enviando la respuesta del servicio */
				if (send(sd_actual, msg, strlen(msg), 0) == -1) {
					perror("send");
					exit(1);
				}

			/* cerrar los dos sockets */
			close(sd_actual);  
			close(sd);
			printf("Conexion cerrada\n");

			
		}else{
			//father
			close(sd_actual);
		}
		return 0;
}